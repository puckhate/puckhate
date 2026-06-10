from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from api.models import SiteStats
from libraries.hockeytech import HockeyTechAPIClient, HockeyTechAPIException


def _to_int(value) -> int:
    """Coerce a stat value to an int, treating anything unparseable as 0."""
    try:
        return int(value)
    except TypeError, ValueError:
        return 0


def total_goals(stats: dict) -> int:
    """Sum goals across every section's "Total" row in a player's career stats"""
    goals = 0
    try:
        for group in stats.get("careerStats", []):
            for section in group.get("sections", []):
                for entry in section.get("data", []):
                    row = entry.get("row", {})
                    if row.get("season_name") == "Total":
                        goals += _to_int(row.get("goals"))
    except AttributeError, TypeError:
        return 0
    return goals


class Command(BaseCommand):
    help = (
        "Fetches the tracked player's career goal total from HockeyTech, "
        "subtracts the starting goal count (goals already scored before the "
        "campaign began), and stores the result on the SiteStats singleton"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch and report the goal total without saving it.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        client = HockeyTechAPIClient(key=settings.HOCKEYTECH_API_KEY)

        try:
            data = client.get_player_stats(
                player_id=settings.HOCKEYTECH_PLAYER_ID,
                season_id=settings.HOCKEYTECH_SEASON_ID,
            )
        except HockeyTechAPIException as exc:
            raise CommandError(f"Failed to fetch player stats: {exc}") from exc

        # Only count goals scored since the campaign began (HOCKEYTECH_STARTING_GOALS)
        career_total = total_goals(data)
        starting_goals = settings.HOCKEYTECH_STARTING_GOALS

        # Don't allow a total count below 0
        goals = max(career_total - starting_goals, 0)

        stats = SiteStats.load()
        current = stats.goals_scored
        goal_detail = f"{career_total} career - {starting_goals} starting"

        if goals <= current:
            self.stdout.write(
                f"Campaign goal total {goals} ({goal_detail}) is not greater than "
                f"the stored {current} - leaving goals_scored unchanged."
            )
            return

        if dry_run:
            self.stdout.write(
                f"[dry-run] would update goals_scored from {current} to {goals} "
                f"({goal_detail})."
            )
            return

        stats.goals_scored = goals
        stats.save(update_fields=["goals_scored"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated goals_scored from {current} to {goals} ({goal_detail})."
            )
        )
