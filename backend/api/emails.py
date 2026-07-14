from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse


def get_donation_review_recipients() -> list[str]:
    """Email addresses for the staff who review donations.

    Active staff members who are either superusers or belong to the
    `approval_admin` group, limited to those with an email on file.
    """
    User = get_user_model()
    return list(
        User.objects.filter(is_active=True, is_staff=True)
        .filter(Q(is_superuser=True) | Q(groups__name="approval_admin"))
        .exclude(email="")
        .order_by("email")
        .values_list("email", flat=True)
        .distinct()
    )


def get_pending_donations_url() -> str:
    """Absolute URL to the admin changelist filtered to pending donations."""
    path = reverse("admin:api_donation_changelist")
    return f"{settings.SITE_URL}{path}?status=pending"


def send_admin_email(
    subject: str, template: str, context: dict, recipients: list[str]
) -> int:
    """Render and send an admin email, returning the number of recipients.

    Args:
        subject: The email subject line.
        template: A base name under `emails/` with both `.html` and `.txt` variants.
        context: A dictionary of template context variables.
        recipients: A list of email addresses to BCC.

    Returns:
        The number of recipients (0 if `recipients` is empty).
    """
    if not recipients:
        return 0

    ctx = {"subject": subject, **context}
    html_body = render_to_string(f"emails/{template}.html", ctx)
    text_body = render_to_string(f"emails/{template}.txt", ctx)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        bcc=recipients,
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
    return len(recipients)
