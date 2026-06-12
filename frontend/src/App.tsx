import { lazy } from "react";

import constants from "@constants";
import { AppLayout } from "@layouts";
import { ExchangeRateProvider } from "@providers/ExchangeRateProvider";
import ErrorView from "@views/ErrorView";
import HomeView from "@views/HomeView/HomeView";
import NotFoundView from "@views/NotFoundView";
import { SkeletonTheme } from "react-loading-skeleton";
import {
  Outlet,
  RouterProvider,
  ScrollRestoration,
  createBrowserRouter,
} from "react-router-dom";

const AboutView = lazy(() => import("@views/AboutView/AboutView"));
const CharitiesView = lazy(() => import("@views/Charities"));
const DisclaimerView = lazy(() => import("@views/Disclaimer"));
const DonationsView = lazy(() => import("@views/Donations"));
const PrivacyView = lazy(() => import("@views/Privacy"));

function Root() {
  return (
    <SkeletonTheme
      baseColor="var(--color-dark-amethyst-900)"
      highlightColor="var(--color-dark-amethyst-800)"
    >
      <ScrollRestoration />
      <Outlet />
    </SkeletonTheme>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    errorElement: <ErrorView />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <HomeView /> },
          { path: constants.ROUTES.about, element: <AboutView /> },
          { path: constants.ROUTES.charities, element: <CharitiesView /> },
          { path: constants.ROUTES.disclaimer, element: <DisclaimerView /> },
          { path: constants.ROUTES.donations, element: <DonationsView /> },
          { path: constants.ROUTES.privacy, element: <PrivacyView /> },
          { path: "*", element: <NotFoundView /> },
        ],
      },
    ],
  },
]);

export default function App() {
  return (
    <ExchangeRateProvider>
      <RouterProvider router={router} />
    </ExchangeRateProvider>
  );
}
