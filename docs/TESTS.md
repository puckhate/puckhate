# Backend tests

Backend tests use Django's built-in test runner. Tests live under `api/tests/`.

## Running

```sh
make test-be                          # whole suite
make test-be ARGS="api.tests.views"   # one package
make test-be ARGS="api.tests.views.test_donations.DonationListTests"  # one class
```

## Writing a test

Subclass `ApiTestCase` (`api/tests/base.py`) and use `self.client` (a Django Rest Framework `APIClient`). The base class neutralizes throttling, page caching, email, and
media storage per test.

```python
from django.urls import reverse

from api.tests.base import ApiTestCase
from api.tests.factories import make_donation


class DonationListTests(ApiTestCase):
    def test_lists_verified_only(self):
        make_donation(verified=True)
        make_donation(verified=False)
        response = self.client.get(reverse("donations"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
```

## Factories

`api/tests/factories.py` leverages [model-bakery](https://model-bakery.readthedocs.io).
Baker fills required fields. Pass any model field as a keyword to override.

```python
from api.tests.factories import make_charity, make_donation, make_receipt, make_staff_user

make_charity()                      # approved charity
make_charity(approved=False)        # proposed charity
make_donation()                     # verified, auto-creates a charity
make_donation(verified=False, amount="10.00", charity=make_charity())
make_receipt()                      # valid in-memory upload, written to temp storage
```

## Mixins

Management commands that call an external API have mixins in
`api/tests/base.py` that patch the client so tests never hit the network. Mix
one in **before** `ApiTestCase` and drive the exposed mock.

### `ExchangeRateAPIMixin`

Patches the CurrencyLayer client used by `update_exchange_rate`. Exposes
`self.mock_get_rate`, which returns a valid CAD rate by default; set its
`return_value` / `side_effect` to steer the command.

```python
from decimal import Decimal

from django.core.management import call_command

from api.models import SiteStats
from api.tests.base import ApiTestCase, ExchangeRateAPIMixin


class UpdateExchangeRateTests(ExchangeRateAPIMixin, ApiTestCase):
    def test_stores_fetched_rate(self):
        self.mock_get_rate.return_value = {"CAD": 1.42}
        call_command("update_exchange_rate")
        self.assertEqual(SiteStats.load().ca_exchange_rate, Decimal("1.4200"))
```

### `HockeyTechAPIMixin`

Patches the HockeyTech client used by `update_goals_scored`. Exposes
`self.mock_get_player_stats`, which returns `{}` by default; set its
`return_value` to a career-stats payload.

```python
from django.core.management import call_command

from api.models import SiteStats
from api.tests.base import ApiTestCase, HockeyTechAPIMixin


class UpdateGoalsScoredTests(HockeyTechAPIMixin, ApiTestCase):
    def test_stores_goal_total(self):
        self.mock_get_player_stats.return_value = {
            "careerStats": [
                {"sections": [{"data": [{"row": {"season_name": "Total", "goals": "40"}}]}]}
            ]
        }
        call_command("update_goals_scored")
        # 40 career − 23 starting (HOCKEYTECH_STARTING_GOALS)
        self.assertEqual(SiteStats.load().goals_scored, 17)
```

## Utilities

### `make_receipt_upload`

Need a raw upload (e.g. to test rejection paths)? Use `make_receipt_upload()`
from `api.tests.base`. Pass `content=` / a bad `filename=` to trip a validator.
