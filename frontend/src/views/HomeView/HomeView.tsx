import { useEffect, useState } from "react";

import client from "@client";
import CONSTANTS from "@constants";
import type { SiteStats } from "@types";

import Hero from "./components/Hero";
import LogDonation from "./components/LogDonation";
import Playbook from "./components/PlaybookCard";

export default function HomeView() {
  const [stats, setStats] = useState<SiteStats | null>(null);
  const [statsLoading, setStatsLoading] = useState<boolean>(true);

  /*
   * Load campaign stats
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<SiteStats>(CONSTANTS.API_ENDPOINTS.STATS, {
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
  return (
    <>
      <Hero
        raised={stats ? Number(stats.verified_total) : undefined}
        donations={stats?.verified_count}
        goals={stats?.goals_scored}
        loading={statsLoading}
      />
      <Playbook />
      <LogDonation />
    </>
  );
}
