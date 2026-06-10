import json
from typing import Dict

import requests

from .exceptions import HockeyTechAPIException


class HockeyTechAPIClient:
    """API client for the HockeyTech API"""

    def __init__(
        self,
        key: str,
        timeout: int = 20,
    ) -> None:
        self.key: str = key
        self.timeout: int = timeout
        self.base_url: str = "https://lscluster.hockeytech.com/feed/index.php"

    def _get_headers(self, *args, **kwargs) -> Dict[str, str]:
        """Return standard request headers, inserting **kwargs as optional additional headers"""
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Referer": "",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        }
        for k in kwargs:
            headers[k] = kwargs[k]
        return headers

    def get_player_stats(
        self,
        player_id: int,
        season_id: int,
        client_code: str = "pwhl",
        lang: str = "en",
    ):
        """Get the player status for a given player_id and season_id"""
        parameters = {
            "feed": "statviewfeed",
            "view": "player",
            "statsType": "standard",
            "category": "seasonstats",
            "key": self.key,
            "player_id": player_id,
            "season_id": season_id,
            "client_code": client_code,
            "lang": lang,
        }
        headers = self._get_headers()
        try:
            response = requests.get(
                self.base_url,
                params=parameters,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise HockeyTechAPIException(str(exc)) from exc

        # response comes back as json enclosed in paretheses
        # string these and then attempt to decode
        try:
            data = response.text[1:-1]
            data = json.loads(data)
            return data
        except AttributeError, TypeError, json.JSONDecodeError:
            return {}


__all__ = ("HockeyTechAPIClient",)
