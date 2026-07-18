import random
from datetime import datetime, timezone

from faker import Faker

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from api.models import Charity, Donation


class Command(BaseCommand):
    help = "Generates seed data (Charities and Donations) for testing purposes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--charities",
            action="store",
            type=int,
            default=0,
            help="Number of verified charities to seed (default: 0)",
        )
        parser.add_argument(
            "--donations",
            action="store",
            type=int,
            default=50,
            help="Number of verified donations to seed (default: 50)",
        )

    def handle(self, *args, **options):
        if settings.SITE_URL == "https://puckhate.com":
            self.stdout.write("This command is not available in production!")
            return

        fake = Faker()

        # Seed verified charities
        if charity_count := options["charities"]:
            self.stdout.write(
                f"Seeding {options['charities']} charit{pluralize(charity_count, 'y,ies')}..."
            )
            for _i in range(charity_count):
                Charity(name=fake.company(), approved=True).save()

        # Seed donations. Will also seed unverified charities if no verified charities exist.
        if donation_count := options["donations"]:
            charity_ids = [charity.id for charity in Charity.objects.all()]  # ty: ignore[unresolved-attribute]

            if not charity_ids:
                self.stdout.write(
                    f"No charities found. Seeding {donation_count} donations with unverified charit{pluralize(donation_count, 'y,ies')}."
                )
                for _i in range(10):
                    charity = Charity(name=fake.company(), approved=False)
                    charity.save()
                    charity_ids.append(charity.id)  # ty: ignore[unresolved-attribute]
            else:
                self.stdout.write(
                    f"Seeding {donation_count} donations with {len(charity_ids)} charit{pluralize(len(charity_ids), 'y,ies')}."
                )
            for _i in range(donation_count):
                chance = random.randint(1, 100)
                Donation(
                    name=fake.name()
                    if chance > 40
                    else "",  # 40% chance to be "Anonymous"
                    amount=random.randint(100, 1000)
                    if chance > 80
                    else random.randint(1, 100),  # 20% chance to be a large donation
                    charity_id=random.choice(charity_ids),
                    verified=datetime.now(tz=timezone.utc),
                ).save()
