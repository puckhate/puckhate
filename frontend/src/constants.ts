const ROUTES = {
  about: "/about",
  charities: "/charities",
  disclaimer: "/disclaimer",
  donations: "/donations",
  home: "/",
  privacy: "/privacy",
  stats: "/stats",
} as const;

export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES] | "*";

export interface RouteMeta {
  title: string;
  description: string;
  robots?: string;
}

const META: Record<RoutePath, RouteMeta> = {
  "/": {
    title: "PUCKHATE!",
    description:
      "A fan-run donation tracker: every goal #77 Britta Curl-Salemme scores becomes a donation supporting the trans community.",
  },
  "/about": {
    title: "The Game Plan | PUCKHATE!",
    description:
      "Who PUCKHATE! is, why PWHL fans decided to answer hate with help, and answers to common questions about how the campaign works.",
  },
  "/charities": {
    title: "Suggested Charities | PUCKHATE!",
    description:
      "Trans-supporting charities suggested by PUCKHATE! fans. Donate directly to one, then report it to add it to the campaign total.",
  },
  "/disclaimer": {
    title: "Disclaimer | PUCKHATE!",
    description:
      "PUCKHATE! is an independent fan project, not affiliated with the PWHL, its teams, or its players, and it does not collect or process donations.",
  },
  "/donations": {
    title: "Donation List | PUCKHATE!",
    description:
      "Every fan-reported donation approved by PUCKHATE! organizers, listed with its charity, amount, and date.",
  },
  "/privacy": {
    title: "Privacy Policy | PUCKHATE!",
    description:
      "How PUCKHATE! handles donation receipts, contact email, and technical logs: what we collect, why we collect it, and how to reach us.",
  },
  "/stats": {
    title: "Campaign Stats | PUCKHATE!",
    description:
      "Running PUCKHATE! campaign totals — amount raised, donations reported, goals answered — alongside current league leaders.",
  },
  "*": {
    title: "Page Not Found | PUCKHATE!",
    description:
      "That page doesn't exist or has moved. Head back to the PUCKHATE! home page.",
    robots: "noindex, follow",
  },
};

const CONSTANTS = {
  API_ENDPOINTS: {
    CHARITIES: `${import.meta.env.VITE_API_BASE_URL}/charities/`,
    DONATIONS: `${import.meta.env.VITE_API_BASE_URL}/donations/`,
    EXCHANGE_RATE: `${import.meta.env.VITE_API_BASE_URL}/exchange-rate/`,
    HEALTH: `${import.meta.env.VITE_API_BASE_URL}/health/`,
    RECEIPTS: `${import.meta.env.VITE_API_BASE_URL}/receipts/`,
    STATS: `${import.meta.env.VITE_API_BASE_URL}/stats/`,
  },
  META,
  ROUTES,
  SOCIAL: {
    bluesky: "https://bsky.app/profile/puckhate.com",
    instagram: "https://www.instagram.com/puckhate",
  },
};

export default CONSTANTS;
