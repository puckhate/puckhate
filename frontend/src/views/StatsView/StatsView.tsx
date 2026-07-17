import { useEffect, useState } from "react";

import client from "@client";
import { Container, H1 } from "@components";
import constants from "@constants";
import type { SiteStats } from "@types";
import { convertFromUSD, getLocaleCurrency } from "@utils/currency";
import { formatAsCurrency, formatAsNumber } from "@utils/text";

import { EmptyStatCard, StatCard } from "./components";

export default function Stats(): React.ReactNode {
  const [stats, setStats] = useState<SiteStats | null>(null);
  const [statsLoading, setStatsLoading] = useState<boolean>(true);

  /*
   * Load campaign stats
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<SiteStats>(constants.API_ENDPOINTS.STATS, {
        signal: controller.signal,
      })
      .then((response) => {
        setStats(response.data);
        setStatsLoading(false);
      })
      .catch(() => {
        // Persist loading state on error, do not raise exception
      });
    return () => controller.abort();
  }, []);

  // Prepare stats calculated in-browser
  const totalRaised = stats
    ? convertFromUSD(
        Number(stats.verified_total),
        Number(stats.ca_exchange_rate),
      )
    : 0;
  const largestDonation = stats
    ? convertFromUSD(
        Number(stats.largest_donation),
        Number(stats.ca_exchange_rate),
      )
    : 0;
  const averageDonation = totalRaised / (stats?.verified_count ?? 1);
  const averageDonationPerGoal =
    (stats?.verified_count ?? 0) / (stats?.goals_scored ?? 1);
  const averageAmountPerGoal = totalRaised / (stats?.goals_scored ?? 1);

  return (
    <Container>
      <article className="space-y-6">
        <header>
          <H1>Stats</H1>
        </header>

        <section>
          <div className="grid grid-cols-2 gap-5 md:grid-cols-3 lg:grid-cols-5">
            <StatCard
              title="Total Donations"
              className="col-span-2 md:col-span-1"
              valueVariant="pink"
              value={formatAsNumber(stats?.verified_count)}
              loading={statsLoading}
            />
            <StatCard
              title={`Total Raised (${getLocaleCurrency().currency})`}
              className="col-span-2"
              value={formatAsCurrency(totalRaised)}
              loading={statsLoading}
            />
            <StatCard
              title={`Avg. Donation (${getLocaleCurrency().currency})`}
              value={formatAsCurrency(averageDonation)}
              loading={statsLoading}
            />
            <StatCard
              title="Avg. Donations per Goal"
              value={formatAsNumber(averageDonationPerGoal)}
              valueVariant="pink"
              loading={statsLoading}
            />
            <StatCard
              title={`Avg. Donation per Goal (${getLocaleCurrency().currency})`}
              value={formatAsCurrency(averageAmountPerGoal)}
              loading={statsLoading}
            />
            <StatCard
              title="Charities Donated To"
              value={formatAsNumber(stats?.charities_donated_to ?? 0)}
              valueVariant="pink"
              loading={statsLoading}
            />
            <StatCard
              title="Largest Donation"
              className="col-span-2"
              value={formatAsCurrency(largestDonation)}
              loading={statsLoading}
            />
            {/* Fill the empty space left by uneven grid count */}
            <EmptyStatCard className="hidden lg:block" loading={statsLoading} />
          </div>
        </section>
      </article>
    </Container>
  );
}
