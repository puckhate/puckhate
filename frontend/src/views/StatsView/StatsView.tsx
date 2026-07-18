import { useEffect, useMemo, useState } from "react";

import client from "@client";
import { Container, H1 } from "@components";
import constants from "@constants";
import { useExchangeRate } from "@providers/ExchangeRateProvider";
import type { Donation, SiteStats } from "@types";
import { convertFromUSD, getLocaleCurrency } from "@utils/currency";
import { formatAsCurrency, formatAsNumber } from "@utils/text";

import { DonorCard, EmptyStatCard, StatCard } from "./components";

export default function Stats(): React.ReactNode {
  const [stats, setStats] = useState<SiteStats | null>(null);
  const [statsLoading, setStatsLoading] = useState<boolean>(true);
  const [donations, setDonations] = useState<Donation[]>([]);
  const [donationsLoading, setDonationsLoading] = useState<boolean>(true);
  const { rate, ensureRate } = useExchangeRate();

  /*
   * Ensure the shared exchange rate is populated for currency conversion
   */
  useEffect(() => {
    ensureRate();
  }, [ensureRate]);

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

  /*
   * Load the top three donations
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<Donation[]>(constants.API_ENDPOINTS.DONATIONS, {
        params: { top: 3 },
        signal: controller.signal,
      })
      .then((response) => {
        setDonations(response.data);
        setDonationsLoading(false);
      })
      .catch(() => {
        // Persist loading state on error, do not raise exception
      });
    return () => controller.abort();
  }, []);

  // Resolve the display currency once per render for the card titles
  const { currency } = useMemo(() => getLocaleCurrency(), []);

  // Prepare stats calculated in-browser
  const exchangeRate = rate ?? 1;
  const totalRaised = stats
    ? convertFromUSD(Number(stats.verified_total), exchangeRate)
    : 0;
  const largestDonation = stats
    ? convertFromUSD(Number(stats.largest_donation), exchangeRate)
    : 0;
  // Guard against division by zero (no donations / no goals yet)
  const verifiedCount = stats?.verified_count ?? 0;
  const goalsScored = stats?.goals_scored ?? 0;
  const averageDonation = verifiedCount ? totalRaised / verifiedCount : 0;
  const averageDonationPerGoal = goalsScored ? verifiedCount / goalsScored : 0;
  const averageAmountPerGoal = goalsScored ? totalRaised / goalsScored : 0;

  return (
    <>
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
                title={`Total Raised (${currency})`}
                className="col-span-2"
                value={formatAsCurrency(totalRaised)}
                loading={statsLoading}
              />
              <StatCard
                title={`Avg. Donation (${currency})`}
                value={formatAsCurrency(averageDonation)}
                className="col-span-2 md:col-span-1"
                loading={statsLoading}
              />
              <StatCard
                title="Avg. Donations per Goal"
                value={formatAsNumber(Math.round(averageDonationPerGoal))}
                valueVariant="pink"
                loading={statsLoading}
              />
              <StatCard
                title="Charities Donated To"
                value={formatAsNumber(stats?.charities_donated_to ?? 0)}
                valueVariant="pink"
                loading={statsLoading}
              />
              <StatCard
                title={`Avg. Donation per Goal (${currency})`}
                className="col-span-2 md:col-span-1"
                value={formatAsCurrency(averageAmountPerGoal)}
                loading={statsLoading}
              />
              <StatCard
                title="Largest Donation"
                className="col-span-2"
                value={formatAsCurrency(largestDonation)}
                loading={statsLoading}
              />
              {/* Fill the empty space left by uneven grid count */}
              <EmptyStatCard
                className="hidden lg:block"
                loading={statsLoading}
              />
            </div>
          </section>
        </article>
      </Container>

      {!donationsLoading && donations.length === 0 ? null : (
        <Container>
          <article className="space-y-6">
            <header>
              <H1>League Leaders</H1>
            </header>
            <section>
              <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
                {donationsLoading
                  ? [1, 2, 3].map((key) => (
                      <DonorCard
                        key={key}
                        loading
                        name="Loading..."
                        amount="Loading..."
                        charity="Loading..."
                      />
                    ))
                  : donations.map((donation, index) => (
                      <DonorCard
                        key={donation.id}
                        name={donation.name}
                        amount={formatAsCurrency(
                          convertFromUSD(Number(donation.amount), exchangeRate),
                        )}
                        charity={donation.charity}
                        rank={index + 1}
                      />
                    ))}
              </div>
            </section>
          </article>
        </Container>
      )}
      <div className="pb-12" />
    </>
  );
}
