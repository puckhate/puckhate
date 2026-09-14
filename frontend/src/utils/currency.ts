/**
 * The locale and currency the prerendered HTML is built with.
 * ExchangeRateProvider swaps to the visitor's locale in an effect,
 * which does not run during hydration.
 */
export const CANONICAL_LOCALE_CURRENCY = {
  locale: "en-US",
  currency: "USD",
};

export interface LocaleCurrency {
  locale: string;
  currency: string;
}

/**
 * Resolve the user's locale and the currency to render in.
 *
 * Return "CAD" for Canadian locale, "USD" for everything else.
 * @returns - the resolved locale and its currency code
 */
export function getLocaleCurrency(): LocaleCurrency {
  const locale =
    (typeof navigator !== "undefined" && navigator.language) ||
    CANONICAL_LOCALE_CURRENCY.locale;
  const { region } = new Intl.Locale(locale).maximize();
  return { locale, currency: region === "CA" ? "CAD" : "USD" };
}

/**
 * Convert a USD amount into the user's display currency.
 *
 * Stored amounts are always USD. US users see them unchanged; CA users see
 * CAD, converted with the current exchange rate.
 * @param usd - amount in USD
 * @param caExchangeRate - Canadian dollars per 1 USD
 * @param currency - the display currency code
 * @returns - amount in the user's display currency
 */
export function convertFromUSD(
  usd: number,
  caExchangeRate: number,
  currency: string,
): number {
  return currency === "CAD" ? usd * caExchangeRate : usd;
}
