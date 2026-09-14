import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import client from "@client";
import constants from "@constants";
import type { ExchangeRate } from "@types";
import {
  CANONICAL_LOCALE_CURRENCY,
  getLocaleCurrency,
  type LocaleCurrency,
} from "@utils/currency";

interface ExchangeRateContextValue extends LocaleCurrency {
  rate: number | null;
  setRate: (rate: number) => void;
  ensureRate: () => void;
}

const ExchangeRateContext = createContext<ExchangeRateContextValue | null>(
  null,
);

/**
 * Shares the exchange rate and display currency across views so amounts
 * (stored in USD) can be localized.
 *
 * The home page populates the rate from its stats call
 * Other views call `ensureRate()` to fetch it from the rate-only endpoint.
 */
export function ExchangeRateProvider({ children }: { children: ReactNode }) {
  const [rate, setRate] = useState<number | null>(null);
  const [localeCurrency, setLocaleCurrency] = useState<LocaleCurrency>(
    CANONICAL_LOCALE_CURRENCY,
  );
  const fetching = useRef<boolean>(false);

  /*
   * Resolve the visitor's locale after mount.
   */
  useEffect(() => {
    setLocaleCurrency(getLocaleCurrency());
  }, []);

  const ensureRate = useCallback(() => {
    if (rate !== null || fetching.current) return;
    fetching.current = true;
    client
      .get<ExchangeRate>(constants.API_ENDPOINTS.EXCHANGE_RATE)
      .then((response) => {
        setRate(Number(response.data.ca_exchange_rate));
      })
      .catch(() => {
        // Leave the rate unset on error
      })
      .finally(() => {
        fetching.current = false;
      });
  }, [rate]);

  const value = useMemo<ExchangeRateContextValue>(
    () => ({ rate, setRate, ensureRate, ...localeCurrency }),
    [rate, ensureRate, localeCurrency],
  );

  return (
    <ExchangeRateContext.Provider value={value}>
      {children}
    </ExchangeRateContext.Provider>
  );
}

export function useExchangeRate(): ExchangeRateContextValue {
  const context = useContext(ExchangeRateContext);
  if (context === null) {
    throw new Error(
      "useExchangeRate must be used within an ExchangeRateProvider",
    );
  }
  return context;
}
