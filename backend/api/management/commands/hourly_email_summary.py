from datetime import timedelta

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize
from django.utils import timezone

from api.emails import (
    get_donation_review_recipients,
    get_pending_donations_url,
    send_admin_email,
)
from api.models import Donation


class Command(BaseCommand):
    help = (
        "Emails approval admins a summary of the donations that entered the "
        "pending-approval queue in the past hour."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be sent without sending any email.",
        )

    def handle(self, *args, **options):
        since = timezone.now() - timedelta(hours=1)
        count = Donation.pending_count(since=since)

        if count == 0:
            self.stdout.write("No new pending donations in the past hour.")
            return

        subject = f"{count} new donation{pluralize(count)} pending review"

        if options["dry_run"]:
            self.stdout.write(f"[dry-run] would email {subject!r} to approval admins.")
            return

        sent = send_admin_email(
            subject=subject,
            recipients=get_donation_review_recipients(),
            template="donations_pending_hourly",
            context={"pending_count": count, "cta_url": get_pending_donations_url()},
        )

        if sent == 0:
            self.stdout.write(
                self.style.WARNING("No approval admins with an email on file.")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent hourly pending-donation summary ({count}) to {sent} admin(s)."
            )
        )
