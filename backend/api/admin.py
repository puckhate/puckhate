from pathlib import Path

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from api.models import Ban, Charity, Donation, DonationReceipt, SiteStats


def receipt_preview(file):
    """Render a receipt file for the admin

    Browser-renderable images become a thumbnail that expands to a larger
    floating preview on hover, other accepted types (heic/heif/pdf)
    fall back to a plain link

    Requires that receipt_admin.css be loaded:
        class Media:
            css = {"all": ("api/receipt_admin.css",)}
    """
    if not file:
        return "—"
    is_image = Path(file.name).suffix.lower() in {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
    }
    return mark_safe(
        render_to_string(
            "admin/api/receipt_preview.html",
            {"url": file.url, "is_image": is_image},
        )
    )


@admin.register(Charity)
class CharityAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "approved", "created")
    list_filter = ("approved",)
    search_fields = ("name", "url")
    actions = ("approve",)

    @admin.action(description="Approve selected charities")
    def approve(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f"Approved {updated} charit(ies).")


@admin.register(DonationReceipt)
class DonationReceiptAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created")
    readonly_fields = ("created", "file", "donation", "file_link")

    class Media:
        css = {"all": ("api/receipt_admin.css",)}

    @admin.display(description="Receipt Preview")
    def file_link(self, obj):
        return receipt_preview(obj.file)

    def has_add_permission(self, request):
        """Receipts cannot be uploaded from the django admin"""
        return False

    def has_change_permission(self, request, obj=None):
        """There is nothing to edit on a receipt, hide save buttons"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Block deleting a receipt that has a verified donation"""
        if obj is not None:
            donations = Donation.objects  # ty: ignore[unresolved-attribute]
            if donations.filter(receipt=obj, verified__isnull=False).exists():
                return False
        return super().has_delete_permission(request, obj)


class VerificationStatusFilter(admin.SimpleListFilter):
    """Filter donations by whether an organizer has approved them"""

    title = "verification status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("approved", "Approved"),
            ("pending", "Pending Review"),
        )

    def queryset(self, request, queryset):
        if self.value() == "approved":
            return queryset.filter(verified__isnull=False)
        if self.value() == "pending":
            return queryset.filter(verified__isnull=True)
        return queryset


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("amount", "name", "charity", "is_verified", "created")
    list_filter = (VerificationStatusFilter,)
    search_fields = ("name",)
    readonly_fields = (
        "created",
        "effective_exchange_rate",
        "verified",
        "verified_by",
        "receipt_link",
        "ip",
    )
    exclude = ("receipt",)
    autocomplete_fields = ("charity",)
    actions = ("approve", "reject", "reject_and_ban")

    class Media:
        css = {"all": ("api/receipt_admin.css",)}

    def response_change(self, request, obj):
        if "_verify" in request.POST:
            if obj.is_verified:
                self.message_user(
                    request, "Donation is already verified.", level=messages.WARNING
                )
            else:
                obj.verified = timezone.now()
                obj.verified_by = request.user
                obj.save(update_fields=["verified", "verified_by"])
                self.message_user(request, "Donation verified.", level=messages.SUCCESS)
            return HttpResponseRedirect(request.get_full_path())
        if "_reject" in request.POST:
            if not self._reject_one(request, obj):
                return HttpResponseRedirect(request.get_full_path())
            self.message_user(request, "Donation rejected.", level=messages.SUCCESS)
            return HttpResponseRedirect(reverse("admin:api_donation_changelist"))
        if "_reject_and_ban" in request.POST:
            # Capture the IP before the donation is deleted.
            ip = obj.ip
            if not self._reject_one(request, obj):
                return HttpResponseRedirect(request.get_full_path())
            if ip:
                self._ban_ip(request, ip)
                self.message_user(
                    request,
                    "Donation rejected and IP banned.",
                    level=messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    "Donation rejected, but no IP on record to ban.",
                    level=messages.WARNING,
                )
            return HttpResponseRedirect(reverse("admin:api_donation_changelist"))
        return super().response_change(request, obj)

    def _ban_ip(self, request, ip) -> bool:
        """Ban `ip` as an admin. Returns True if a new Ban row was created."""
        _, created = Ban.objects.get_or_create(  # ty: ignore[unresolved-attribute]
            ip=ip,
            defaults={
                "type": Ban.Type.ADMIN,
                "reason": "Banned by admin",
                "banned_by": request.user,
            },
        )
        return created

    def _reject_one(self, request, obj) -> bool:
        """Delete a single draft donation.

        Returns False (and warns) if the donation is verified and so cannot be
        rejected; the caller is responsible for the redirect.
        """
        if obj.is_verified:
            self.message_user(
                request,
                "Cannot reject a verified donation.",
                level=messages.ERROR,
            )
            return False
        obj.delete()
        return True

    def _reject_drafts(self, request, queryset):
        """Delete the unverified donations in `queryset`, warn about the rest.

        Returns (deleted_count, ips) where `ips` is the set of non-null IPs the
        deleted drafts carried, so a caller can ban them.
        """
        drafts = queryset.filter(verified__isnull=True)
        skipped = queryset.filter(verified__isnull=False).count()
        # Capture IPs before deletion.
        ips = {ip for ip in drafts.values_list("ip", flat=True) if ip}
        deleted = drafts.count()
        drafts.delete()
        if skipped:
            self.message_user(
                request,
                f"Skipped {skipped} verified donation(s); verified donations "
                "cannot be rejected.",
                level=messages.WARNING,
            )
        return deleted, ips

    @admin.display(boolean=True, description="Verified")
    def is_verified(self, obj):
        return obj.is_verified

    @admin.display(description="Receipt Preview")
    def receipt_link(self, obj):
        if not obj.receipt_id:
            return "—"
        return receipt_preview(obj.receipt.file)

    @admin.action(description="Approve selected donations")
    def approve(self, request, queryset):
        updated = queryset.filter(verified__isnull=True).update(
            verified=timezone.now(), verified_by=request.user
        )
        self.message_user(request, f"Approved {updated} donation(s).")

    @admin.action(description="Reject selected donations")
    def reject(self, request, queryset):
        deleted, _ = self._reject_drafts(request, queryset)
        self.message_user(request, f"Rejected {deleted} donation(s).")

    @admin.action(description="Reject and ban selected donations")
    def reject_and_ban(self, request, queryset):
        deleted, ips = self._reject_drafts(request, queryset)
        banned = sum(self._ban_ip(request, ip) for ip in ips)
        self.message_user(
            request, f"Rejected {deleted} donation(s) and banned {banned} IP(s)."
        )


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ("ip", "type", "reason", "created")
    list_filter = ("type",)
    search_fields = ("ip", "reason")
    readonly_fields = ("created",)


@admin.register(SiteStats)
class SiteStatsAdmin(admin.ModelAdmin):
    """Singleton: no adding a second row, no deleting the one row."""

    def has_add_permission(self, request):
        return not SiteStats.objects.exists()  # ty: ignore[unresolved-attribute]

    def has_delete_permission(self, request, obj=None):
        return False
