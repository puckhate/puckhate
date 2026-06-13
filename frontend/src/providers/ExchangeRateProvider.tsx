import {
  type ReactNode,
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";

import client from "@client";
import constants from "@constants";
import type { ExchangeRate } from "@types";

interface ExchangeRateContextValue {
  rate: number | null;
  setRate: (rate: number) => void;
  ensureRate: () => void;
}

const ExchangeRateContext = createContext<ExchangeRateContextValue | null>(
  null,
);

/**
 * Shares the exchange rate across views so amounts (stored in USD)
 * can be localized without each page refetching it.
 *
 * The home page populates it from its stats call
 * Other views call `ensureRate()` to fetch it from the rate-only endpoint.
 */
export function ExchangeRateProvider({ children }: { children: ReactNode }) {
  const [rate, setRate] = useState<number | null>(null);
  const fetching = useRef<boolean>(false);

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
    () => ({ rate, setRate, ensureRate }),
    [rate, ensureRate],
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
