import logging
import uuid
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import storages
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class Charity(models.Model):
    """A charity fans can attribute a donation to.

    Fans may propose a new charity from the log-donation form. It is created
    with `approved=False` and an admin reviews/approves it before it
    appears in any public charity listing or typeahead.
    """

    name = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "charities"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @classmethod
    def approved_charities(cls):
        return cls.objects.filter(approved=True)  # ty: ignore[unresolved-attribute]


def make_receipt_path(instance, filename):
    """Store receipts under <private root>/receipts/ with an opaque filename"""
    ext = Path(filename).suffix.lower()
    return f"receipts/{uuid.uuid4().hex}{ext}"


def select_private_storage():
    """Return the private storage backend for receipt uploads"""
    return storages["private"]


class DonationReceipt(models.Model):
    """An uploaded proof-of-donation file (image or PDF).

    Created independently of a Donation so the frontend can transfer the
    file as soon as it is dropped while the user finishes the form. A receipt
    that is never claimed by a Donation is an orphan and will be reaped by a
    periodic cleanup job.
    """

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to=make_receipt_path,
        storage=select_private_storage,
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Receipt {self.pk} ({self.created:%Y-%m-%d})"


class Donation(models.Model):
    """A fan-reported donation.

    Lives as a draft until an admin approves it.
    Only verified donations roll up into the public totals.
    """

    created = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    effective_exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal("1.0000"),
        help_text=("Canadian dollars per 1 USD applied when this donation was stored"),
    )
    receipt = models.OneToOneField(
        DonationReceipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donation",
    )
    name = models.CharField(max_length=255, blank=True)
    charity = models.ForeignKey(
        Charity,
        on_delete=models.PROTECT,
        related_name="donations",
    )
    verified = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_donations",
    )

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["verified"])]

    def __str__(self):
        state = "verified" if self.is_verified else "draft"
        return f"${self.amount} from {self.get_name_display()} ({state})"

    def get_name_display(self):
        """Donor name for display, falling back to "Anonymous" when blank."""
        return self.name or "Anonymous"

    @property
    def is_verified(self):
        return self.verified is not None

    @classmethod
    def verified_total(cls):
        """Sum of `amount` across all verified donations"""
        total = cls.objects.filter(verified__isnull=False).aggregate(  # ty: ignore[unresolved-attribute]
            total=models.Sum("amount")
        )["total"]
        return total or Decimal("0")

    @classmethod
    def verified_count(cls):
        """Total number of verified donations"""
        return cls.objects.filter(verified__isnull=False).count()  # ty: ignore[unresolved-attribute]

    @classmethod
    def verified_donations(cls):
        """Verified donations, most-recently-verified first."""
        return (
            cls.objects.filter(verified__isnull=False)  # ty: ignore[unresolved-attribute]
            .select_related("charity")
            .order_by("-verified")
        )


class SiteStats(models.Model):
    """Singleton of display stats shown on the public site.

    Access via SiteStats.load().
    """

    goals_scored = models.PositiveIntegerField(default=0)
    ca_exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal("1.0000"),
        validators=[MinValueValidator(Decimal("0.0001"))],
        help_text=("Canadian dollars per 1 USD."),
    )

    class Meta:
        verbose_name = "site stats"
        verbose_name_plural = "site stats"

    def __str__(self):
        return "Site stats"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Do not allow delete of a singleton value"""

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)  # ty: ignore[unresolved-attribute]
        return obj


@receiver(post_delete, sender=Donation)
def delete_receipt_with_donation(sender, instance, **kwargs):
    """Deleting a donation must also remove its receipt."""
    if not instance.receipt_id:
        return
    try:
        instance.receipt.delete()
    except ObjectDoesNotExist:
        pass


@receiver(post_delete, sender=DonationReceipt)
def delete_receipt_file(sender, instance, **kwargs):
    """Remove the physical file when a receipt row is deleted."""
    if not instance.file:
        return
    try:
        instance.file.delete(save=False)
    except OSError as exc:
        logger.warning("Could not delete receipt file %r: %s", instance.file.name, exc)
