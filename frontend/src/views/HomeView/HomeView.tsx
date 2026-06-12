import { useEffect, useState } from "react";

import client from "@client";
import CONSTANTS from "@constants";
import { useExchangeRate } from "@providers/ExchangeRateProvider";
import type { Charity, SiteStats } from "@types";
import { convertFromUSD } from "@utils/currency";

import Hero from "./components/Hero";
import LogDonation from "./components/LogDonation";
import Playbook from "./components/PlaybookCard";

export default function HomeView() {
  const [stats, setStats] = useState<SiteStats | null>(null);
  const [statsLoading, setStatsLoading] = useState<boolean>(true);
  const [charities, setCharities] = useState<Charity[]>([]);
  const { setRate } = useExchangeRate();

  /*
   * Load campaign stats
   * Set the exchange rate in context to speed up other views
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<SiteStats>(CONSTANTS.API_ENDPOINTS.STATS, {
        signal: controller.signal,
      })
      .then((response) => {
        setStats(response.data);
        setRate(Number(response.data.ca_exchange_rate));
        setStatsLoading(false);
      })
      .catch(() => {
        // Persist loading state on error, do not raise exception
      });
    return () => controller.abort();
  }, [setRate]);

  /*
   * Load approved charities to share with the playbook and donation form.
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<Charity[]>(CONSTANTS.API_ENDPOINTS.CHARITIES, {
        signal: controller.signal,
      })
      .then((response) => {
        setCharities(response.data);
      })
      .catch(() => {
        // Suggestions are optional, ignore failures.
      });
    return () => controller.abort();
  }, []);

  return (
    <>
      <Hero
        raised={
          stats
            ? convertFromUSD(
                Number(stats.verified_total),
                Number(stats.ca_exchange_rate),
              )
            : undefined
        }
        donations={stats?.verified_count}
        goals={stats?.goals_scored}
        loading={statsLoading}
      />
      <Playbook charities={charities} />
      <LogDonation charities={charities} />
    </>
  );
}
