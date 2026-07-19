const CONSTANTS = {
  API_ENDPOINTS: {
    CHARITIES: `${import.meta.env.VITE_API_BASE_URL}/charities/`,
    DONATIONS: `${import.meta.env.VITE_API_BASE_URL}/donations/`,
    EXCHANGE_RATE: `${import.meta.env.VITE_API_BASE_URL}/exchange-rate/`,
    HEALTH: `${import.meta.env.VITE_API_BASE_URL}/health/`,
    RECEIPTS: `${import.meta.env.VITE_API_BASE_URL}/receipts/`,
    STATS: `${import.meta.env.VITE_API_BASE_URL}/stats/`,
  },
  ROUTES: {
    about: "/about",
    charities: "/charities",
    disclaimer: "/disclaimer",
    donations: "/donations",
    home: "/",
    privacy: "/privacy",
    stats: "/stats",
  },
  SOCIAL: {
    bluesky: "https://bsky.app/profile/puckhate.com",
    instagram: "https://www.instagram.com/puckhate",
  },
};

export default CONSTANTS;
