import { lazy } from "react";

import constants from "@constants";
import { AppLayout } from "@layouts";
import HomeView from "@views/HomeView/HomeView";
import NotFoundView from "@views/NotFoundView";
import {
  Outlet,
  RouterProvider,
  ScrollRestoration,
  createBrowserRouter,
} from "react-router-dom";
import { ToastContainer } from "react-toastify";

const Privacy = lazy(() => import("@views/Privacy"));
const Disclaimer = lazy(() => import("@views/Disclaimer"));
const Charities = lazy(() => import("@views/Charities"));
const Plan = lazy(() => import("@views/Plan"));

function Root() {
  return (
    <>
      <ScrollRestoration />
      <Outlet />
      <ToastContainer
        position="top-right"
        pauseOnFocusLoss={false}
        toastClassName="text-sm"
        closeOnClick
        pauseOnHover
      />
    </>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <HomeView /> },
          { path: constants.ROUTES.charities, element: <Charities /> },
          { path: constants.ROUTES.plan, element: <Plan /> },
          { path: constants.ROUTES.privacy, element: <Privacy /> },
          { path: constants.ROUTES.disclaimer, element: <Disclaimer /> },
          { path: "*", element: <NotFoundView /> },
        ],
      },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
