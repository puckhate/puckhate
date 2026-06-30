from typing import Dict, List, Union

import requests

from .exceptions import CurrencyLayerAPIException


class CurrencyLayerAPIClient:
    """API client for the Currency Layer API"""

    def __init__(
        self,
        api_key: str,
        timeout: int = 20,
    ) -> None:
        self.api_key: str = api_key
        self.timeout: int = timeout
        self.base_url: str = "https://api.currencylayer.com"

    def _get_headers(self, *args, **kwargs) -> Dict[str, str]:
        """Return standard request headers, inserting **kwargs as optional additional headers"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-cache",
            "User-Agent": "PUCKHATE API/1.0",
        }
        for k in kwargs:
            headers[k] = kwargs[k]
        return headers

    def _get_full_url(self, path: str) -> str:
        """Build a full calling URL, given a path and a base_url.

        Args:
            path (str): URL path for service
        """
        return f"{self.base_url}/{path}"

    def get_rate(
        self,
        from_currency: str,
        to_currency: Union[str, List[str]],
    ) -> Dict[str, float]:
        """Get the exchange rate from one currency into one or more others.

        Args:
            from_currency (str): the source currency code (e.g. "USD").
            to_currency (str | list[str]): one or more target currency codes
                (e.g. "CAD" or ["CAD", "EUR"]).

        Returns:
            A dict mapping each target currency code to its rate, e.g.
            ``{"CAD": 1.7312}``.

        Raises:
            CurrencyLayerAPIException: on a transport error, a non-2xx
                response, or an unsuccessful API result.
        """
        currencies = (
            [to_currency] if isinstance(to_currency, str) else list(to_currency)
        )

        parameters = {
            "access_key": self.api_key,
            "currencies": ",".join(currencies),
            "source": from_currency,
        }
        url = self._get_full_url("live")
        headers = self._get_headers()

        try:
            response = requests.get(
                url,
                params=parameters,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CurrencyLayerAPIException(str(exc)) from exc

        data = response.json()

        if not data.get("success"):
            error = data.get("error", {})
            raise CurrencyLayerAPIException(
                error.get("info") or "CurrencyLayer request was unsuccessful"
            )

        source = data.get("source", from_currency)
        quotes = data.get("quotes", {})

        # Quote keys concatenate the source and target codes (e.g. "USDCAD");
        # strip the source prefix to key the result by the target alone.
        return {
            pair[len(source) :]: rate
            for pair, rate in quotes.items()
            if pair.startswith(source)
        }


__all__ = ("CurrencyLayerAPIClient",)
