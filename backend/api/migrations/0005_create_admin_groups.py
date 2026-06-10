from django.contrib.auth.management import create_permissions
from django.db import migrations

# Organizer groups and the `api` model permissions each one grants
GROUP_PERMISSIONS = {
    # Approve/reject donations and view/delete their receipts.
    "approval_admin": {
        "donation": ["add", "change", "delete", "view"],
    },
    # Full admin actions on charities
    "charity_admin": {
        "charity": ["add", "change", "delete", "view"],
    },
    # Everything in the api app (charities, receipts, donations, stats),
    # but nothing in auth (users/groups).
    "full_admin": {
        "charity": ["add", "change", "delete", "view"],
        "donation": ["add", "change", "delete", "view"],
        "donationreceipt": ["add", "change", "delete", "view"],
        "sitestats": ["change", "view"],
    },
    # View and change site stats
    "stats_admin": {
        "sitestats": ["view", "change"],
    },
}


def ensure_api_permissions():
    from django.apps import apps as global_apps

    app_config = global_apps.get_app_config("api")
    app_config.models_module = app_config.models_module or True
    create_permissions(app_config, verbosity=0)


def create_groups(apps, schema_editor):
    ensure_api_permissions()
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for group_name, model_perms in GROUP_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        codenames = [
            f"{action}_{model}"
            for model, actions in model_perms.items()
            for action in actions
        ]
        perms = Permission.objects.filter(
            content_type__app_label="api", codename__in=codenames
        )
        group.permissions.set(perms)


def delete_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=GROUP_PERMISSIONS.keys()).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0004_donationreceipt_token_and_rate_validator"),
        ("auth", "__first__"),
        ("contenttypes", "__first__"),
    ]

    operations = [
        migrations.RunPython(create_groups, delete_groups),
    ]
