from django.db import migrations

SEED_CHARITIES = [
    ("The Trevor Project", "https://www.thetrevorproject.org/"),
    ("Black Leaders Detroit", "https://www.blackleadersdetroit.org/"),
    ("Out Front Kalamazoo", "https://www.outfrontkzoo.org/"),
    ("ACLU of Michigan", "https://www.aclumich.org/"),
    ("Black United Fund of Michigan", "https://www.bufmi.org/"),
    ("Affirmations", "https://goaffirmations.org/"),
    ("Ferncare Free Clinic", "https://ferncare.org/"),
    ("LGBT Detroit", "https://www.lgbtdetroit.org/"),
    ("Ruth Ellis Center", "https://www.ruthelliscenter.org/"),
    ("The Corner Health Center", "https://cornerhealth.org/"),
    ("Jim Toy Community Center", "https://www.jimtoycenter.org/"),
    ("Ozone House", "https://ozonehouse.org/"),
    ("Keep Growing Detroit", "https://www.detroitagriculture.net/"),
]


def seed_charities(apps, schema_editor):
    Charity = apps.get_model("api", "Charity")
    for name, url in SEED_CHARITIES:
        Charity.objects.update_or_create(
            name=name,
            defaults={"url": url, "approved": True},
        )


def unseed_charities(apps, schema_editor):
    Charity = apps.get_model("api", "Charity")
    names = [name for name, _ in SEED_CHARITIES]
    Charity.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_charities, unseed_charities),
    ]
