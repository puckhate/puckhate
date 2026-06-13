import { useEffect, useState } from "react";

import client from "@client";
import { Container } from "@components";
import constants from "@constants";
import { useExchangeRate } from "@providers/ExchangeRateProvider";
import type { Charity, SiteStats } from "@types";
import { convertFromUSD } from "@utils/currency";

import Hero from "./components/Hero";
import LogDonation from "./components/LogDonation";
import Playbook from "./components/Playbook";

const sectionPadding = "py-6 md:py-12 xl:py-20";

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
      .get<SiteStats>(constants.API_ENDPOINTS.STATS, {
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
      .get<Charity[]>(constants.API_ENDPOINTS.CHARITIES, {
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
      {/* Content broken into three Containers instead of one, playbook exceeds standard Container width */}
      <Container className={sectionPadding}>
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
      </Container>
      {/* Playbook has a full-width dark background that overflows the standard Container */}
      <div className="bg-dark-amethyst-950/70">
        <Container className={sectionPadding}>
          <Playbook charities={charities} />
        </Container>
      </div>
      <Container className={sectionPadding}>
        <LogDonation charities={charities} />
      </Container>
    </>
  );
}
