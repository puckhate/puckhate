from datetime import timedelta
from io import StringIO

from django.core import mail
from django.core.management import call_command
from django.utils import timezone

from api.tests.base import ApiTestCase
from api.tests.factories import make_donation, make_user


class DailyEmailSummaryTests(ApiTestCase):
    """manage.py daily_email_summary"""

    def run_command(self, *args):
        call_command("daily_email_summary", *args, stdout=StringIO())

    def test_does_not_send_when_nothing_pending(self):
        """Verified donations are not pending, so nothing is emailed."""
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=True)
        self.run_command()
        self.assertEqual(len(mail.outbox), 0)

    def test_sends_when_pending(self):
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=False)
        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].bcc, ["admin@example.com"])

    def test_counts_only_unverified_donations(self):
        """The subject count reflects pending drafts, ignoring verified ones."""
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=False, _count=3)
        make_donation(verified=True, _count=2)
        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("3", mail.outbox[0].subject)

    def test_counts_pending_regardless_of_age(self):
        """Unlike the hourly summary, the daily count ignores creation time."""
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=False, created=timezone.now() - timedelta(days=5))
        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("1", mail.outbox[0].subject)

    def test_only_eligible_admins_are_recipients(self):
        """Recipients are active staff who are superusers or approval_admins
        and who have an email on file. Everyone else is excluded."""
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_user(
            email="group@example.com",
            is_staff=True,
            groups=[
                "approval_admin",
            ],
        )
        # Ineligible for various reasons:
        make_user(email="", is_staff=True, is_superuser=True)  # no email
        make_user(email="notstaff@example.com", is_superuser=True)  # not staff
        make_user(  # inactive
            email="inactive@example.com",
            is_staff=True,
            is_superuser=True,
            is_active=False,
        )
        make_user(email="plainstaff@example.com", is_staff=True)  # not a reviewer
        make_donation(verified=False)
        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertCountEqual(
            mail.outbox[0].bcc, ["admin@example.com", "group@example.com"]
        )

    def test_deduplicates_recipient_matching_both_rules(self):
        """A superuser who is also in approval_admin is BCC'd only once."""
        make_user(
            email="both@example.com",
            is_staff=True,
            is_superuser=True,
            groups=["approval_admin"],
        )
        make_donation(verified=False)
        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].bcc, ["both@example.com"])

    def test_does_not_send_without_eligible_recipients(self):
        """Pending donations but no reviewer with an email -> no mail sent."""
        make_user(email="plainstaff@example.com", is_staff=True)  # not a reviewer
        make_donation(verified=False)
        self.run_command()
        self.assertEqual(len(mail.outbox), 0)

    def test_dry_run_sends_nothing(self):
        """--dry-run reports the summary but sends no email."""
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=False)
        self.run_command("--dry-run")
        self.assertEqual(len(mail.outbox), 0)


class HourlyEmailSummaryTests(ApiTestCase):
    """manage.py hourly_email_summary"""

    def run_command(self, *args):
        call_command("hourly_email_summary", *args, stdout=StringIO())

    def test_sends_for_pending_in_last_hour(self):
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=False)
        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].bcc, ["admin@example.com"])
        self.assertIn("1", mail.outbox[0].subject)

    def test_ignores_pending_older_than_an_hour(self):
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=False, created=timezone.now() - timedelta(hours=2))
        self.run_command()
        self.assertEqual(len(mail.outbox), 0)

    def test_ignores_recent_verified_donations(self):
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=True)
        self.run_command()
        self.assertEqual(len(mail.outbox), 0)

    def test_counts_only_recent_unverified_donations(self):
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=False, _count=2)
        make_donation(verified=False, created=timezone.now() - timedelta(hours=2))
        make_donation(verified=True)
        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("2", mail.outbox[0].subject)

    def test_dry_run_sends_nothing(self):
        """--dry-run reports the summary but sends no email."""
        make_user(email="admin@example.com", is_staff=True, is_superuser=True)
        make_donation(verified=False)
        self.run_command("--dry-run")
        self.assertEqual(len(mail.outbox), 0)
