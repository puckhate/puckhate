from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from api.emails import (
    get_donation_review_recipients,
    get_pending_donations_url,
    send_admin_email,
)
from api.models import Donation


class Command(BaseCommand):
    help = (
        "Emails approval admins the total number of donations currently "
        "pending review, regardless of when they were created."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be sent without sending any email.",
        )

    def handle(self, *args, **options):
        count = Donation.pending_count()

        if count == 0:
            self.stdout.write("No donations pending review.")
            return

        subject = f"{count} donation{pluralize(count)} pending review"

        if options["dry_run"]:
            self.stdout.write(f"[dry-run] would email {subject!r} to approval admins.")
            return

        sent = send_admin_email(
            subject=subject,
            recipients=get_donation_review_recipients(),
            template="donations_pending_daily",
            context={"pending_count": count, "cta_url": get_pending_donations_url()},
        )

        if sent == 0:
            self.stdout.write(
                self.style.WARNING("No approval admins with an email on file.")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent daily pending-donation summary ({count}) to {sent} admin(s)."
            )
        )
