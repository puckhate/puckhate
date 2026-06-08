const CONSTANTS = {
  API_ENDPOINTS: {
    HEALTH: `${import.meta.env.VITE_API_BASE_URL}/health/`,
    STATS: `${import.meta.env.VITE_API_BASE_URL}/stats/`,
    DONATIONS: `${import.meta.env.VITE_API_BASE_URL}/donations/`,
    RECEIPTS: `${import.meta.env.VITE_API_BASE_URL}/receipts/`,
    CHARITIES: `${import.meta.env.VITE_API_BASE_URL}/charities/`,
  },
  ROUTES: {
    home: "/",
    privacy: "/privacy",
    disclaimer: "/disclaimer",
    charities: "/charities",
    donations: "/donations",
    plan: "/plan",
  },
  SOCIAL: {
    bluesky: "https://bsky.app/profile/puckcurl.bsky.social",
    discord: "https://discord.gg/xKkQ8RpXMh",
    instagram: "https://www.instagram.com/puckcurl",
  },
};

export default CONSTANTS;
