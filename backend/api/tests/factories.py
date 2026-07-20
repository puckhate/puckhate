from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal

from model_bakery import baker

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from api.models import Charity, Donation, DonationReceipt
from api.tests.base import make_receipt_upload


def _bake(model, *, created: datetime | None, _count: int | None, **overrides):
    """Wrap baker.make(), optionally backdating `created`, and/or creating multiple instances.

    Args:
        created: Optional datetime to backdate `created` to after creation.
        _count: Optional number of instances to create
        **overrides: Optional keyword arguments to pass to `baker.make()`.
    """

    def _set_created(obj, created: datetime | None):
        """Backdate `created` after creation."""
        if created is not None:
            type(obj).objects.filter(pk=obj.pk).update(created=created)
            obj.created = created
        return obj

    if _count is not None:
        return [
            _set_created(obj, created)
            for obj in baker.make(model, _quantity=_count, **overrides)
        ]
    return _set_created(baker.make(model, **overrides), created)


def make_charity(
    *, created: datetime | None = None, _count: int | None = None, **overrides
) -> Charity | list[Charity]:
    """Create a Charity

    Args:
        approved: Optional boolean indicating whether the charity is approved. Defaults to True.
        created: Optional datetime to backdate `created` to after creation.
        _count: Optional number of instances to create
        **overrides: Optional keyword arguments to pass to `baker.make()`.
    """
    overrides.setdefault("approved", True)
    return _bake(Charity, created=created, _count=_count, **overrides)


def make_receipt(
    *, created: datetime | None = None, _count: int | None = None, **overrides
) -> DonationReceipt | list[DonationReceipt]:
    """Create a DonationReceipt, backed by a valid in-memory upload.

    Args:
        created: Optional datetime to backdate `created` to after creation.
        _count: Optional number of instances to create
        **overrides: Optional keyword arguments to pass to `baker.make()`.

    Note:
        With `_count`, every receipt shares the one default upload object, so
        only the first ends up with file bytes on disk.
    """
    overrides.setdefault("file", make_receipt_upload())
    return _bake(DonationReceipt, created=created, _count=_count, **overrides)


def make_donation(
    *,
    verified: bool = True,
    created: datetime | None = None,
    _count: int | None = None,
    **overrides,
) -> Donation | list[Donation]:
    """Create a Donation.

    Args:
        verified: Optional boolean indicating whether the donation is verified. Defaults to True.
        created: Optional datetime to backdate `created` to after creation.
        _count: Optional number of instances to create
        **overrides: Optional keyword arguments to pass to `baker.make()`.

    Note:
        Creates a charity unless given.

    """
    overrides.setdefault("amount", Decimal("25.00"))
    overrides.setdefault("verified", timezone.now() if verified else None)
    return _bake(Donation, created=created, _count=_count, **overrides)


def make_user(*, groups: Iterable[str] = (), **overrides):
    """Create a User.

    Args:
        groups: Optional iterable of group names to add to the user.
        **overrides: Optional keyword arguments to pass to `baker.make()`.

    Note:
        By default, `is_staff` and `is_superuser` are set to `False`, and
        `is_active` is set to `True`.
    """
    User = get_user_model()
    overrides.setdefault("email", "")
    user = baker.make(User, **overrides)
    for name in groups:
        group, _ = Group.objects.get_or_create(name=name)
        user.groups.add(group)
    return user
