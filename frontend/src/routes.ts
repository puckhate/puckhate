import {
  index,
  layout,
  type RouteConfig,
  route,
} from "@react-router/dev/routes";

export default [
  layout("layouts/AppLayout.tsx", [
    index("views/HomeView/HomeView.tsx"),
    route("about", "views/AboutView/AboutView.tsx"),
    route("charities", "views/CharitiesView.tsx"),
    route("disclaimer", "views/DisclaimerView.tsx"),
    route("donations", "views/DonationsView.tsx"),
    route("privacy", "views/PrivacyView.tsx"),
    route("stats", "views/StatsView/StatsView.tsx"),
    route("*", "views/NotFoundView.tsx"),
  ]),
] satisfies RouteConfig;
