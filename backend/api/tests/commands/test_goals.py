from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from api.models import SiteStats
from api.tests.base import ApiTestCase, HockeyTechAPIMixin
from libraries.hockeytech import HockeyTechAPIException


def career_stats(*total_goals: object) -> dict:
    """Generate a mock HockeyTech response payload."""
    return {
        "careerStats": [
            {
                "sections": [
                    {
                        "data": [
                            {"row": {"season_name": "Total", "goals": goals}}
                            for goals in total_goals
                        ]
                    }
                ]
            }
        ]
    }


@override_settings(
    HOCKEYTECH_API_KEY="test-key",
    HOCKEYTECH_PLAYER_ID=1,
    HOCKEYTECH_SEASON_ID=1,
    HOCKEYTECH_STARTING_GOALS=0,
)
class UpdateGoalsScoredCommandTests(HockeyTechAPIMixin, ApiTestCase):
    """manage.py update_goals_scored"""

    def run_command(self, *args):
        call_command("update_goals_scored", *args, stdout=StringIO())

    def current_goals(self) -> int:
        return SiteStats.load().goals_scored

    def set_goals(self, value: int):
        stats = SiteStats.load()
        stats.goals_scored = value
        stats.save(update_fields=["goals_scored"])

    def test_updates_when_total_increases(self):
        self.mock_get_player_stats.return_value = career_stats(10)
        self.run_command()
        self.assertEqual(self.current_goals(), 10)

    @override_settings(HOCKEYTECH_STARTING_GOALS=3)
    def test_subtracts_starting_goals(self):
        """Only goals scored since the campaign began are counted."""
        self.mock_get_player_stats.return_value = career_stats(10)
        self.run_command()
        self.assertEqual(self.current_goals(), 7)

    def test_does_not_decrease_stored_total(self):
        """A lower fetched total never lowers goals_scored."""
        self.set_goals(20)
        self.mock_get_player_stats.return_value = career_stats(10)
        self.run_command()
        self.assertEqual(self.current_goals(), 20)

    def test_leaves_unchanged_when_equal(self):
        """A total equal to the stored value is not written (strictly-greater)."""
        self.set_goals(10)
        self.mock_get_player_stats.return_value = career_stats(10)
        self.run_command()
        self.assertEqual(self.current_goals(), 10)

    @override_settings(HOCKEYTECH_STARTING_GOALS=5)
    def test_clamps_negative_to_zero(self):
        """career < starting yields 0, never a negative count."""
        self.mock_get_player_stats.return_value = career_stats(2)
        self.run_command()
        self.assertEqual(self.current_goals(), 0)

    def test_sums_only_total_rows_across_sections(self):
        """Total rows are summed; non-Total rows are ignored."""
        self.mock_get_player_stats.return_value = {
            "careerStats": [
                {
                    "sections": [
                        {
                            "data": [
                                {"row": {"season_name": "2024-25", "goals": 99}},
                                {"row": {"season_name": "Total", "goals": 8}},
                            ]
                        },
                        {"data": [{"row": {"season_name": "Total", "goals": 4}}]},
                    ]
                }
            ]
        }
        self.run_command()
        self.assertEqual(self.current_goals(), 12)

    def test_unparseable_goal_value_counts_as_zero(self):
        self.mock_get_player_stats.return_value = career_stats("x", 6)
        self.run_command()
        self.assertEqual(self.current_goals(), 6)

    def test_garbled_response_is_treated_as_zero(self):
        """Malformed data is handled gracefully and leaves the total alone."""
        self.set_goals(5)
        self.mock_get_player_stats.return_value = {"careerStats": "not-a-list"}
        self.run_command()
        self.assertEqual(self.current_goals(), 5)

    def test_api_exception_leaves_goals_unchanged(self):
        self.set_goals(5)
        self.mock_get_player_stats.side_effect = HockeyTechAPIException("boom")
        with self.assertRaises(CommandError):
            self.run_command()
        self.assertEqual(self.current_goals(), 5)

    def test_dry_run_does_not_save(self):
        self.mock_get_player_stats.return_value = career_stats(10)
        self.run_command("--dry-run")
        self.assertEqual(self.current_goals(), 0)
