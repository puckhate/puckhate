import { StrictMode } from "react";

import { ExchangeRateProvider } from "@providers/ExchangeRateProvider";
import { asset } from "@utils/asset";
import { routeMeta } from "@utils/meta";
import ErrorView from "@views/ErrorView";
import { SkeletonTheme } from "react-loading-skeleton";
import {
  Links,
  type LinksFunction,
  Meta,
  type MetaFunction,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";

import "./index.css";

// All views delcare their own meta - so only handle the fallback here
export const meta: MetaFunction = () => routeMeta("*");

export const links: LinksFunction = () => [
  // Montserrat renders the headline
  {
    rel: "preload",
    href: asset("fonts/montserrat-latin-v1.woff2"),
    as: "font",
    type: "font/woff2",
    crossOrigin: "anonymous",
  },
  { rel: "manifest", href: asset("site.webmanifest") },
  {
    rel: "icon",
    type: "image/png",
    sizes: "32x32",
    href: asset("favicon-32x32.png"),
  },
  {
    rel: "icon",
    type: "image/png",
    sizes: "16x16",
    href: asset("favicon-16x16.png"),
  },
  {
    rel: "apple-touch-icon",
    sizes: "180x180",
    href: asset("apple-touch-icon.png"),
  },
  { rel: "icon", type: "image/x-icon", href: asset("favicon.ico") },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="bg-page h-full">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="theme-color" content="#0C062D" />
        <Meta />
        <Links />
      </head>
      <body className="h-full" suppressHydrationWarning>
        <StrictMode>{children}</StrictMode>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function Root(): React.ReactNode {
  return (
    <ExchangeRateProvider>
      <SkeletonTheme
        baseColor="var(--color-dark-amethyst-900)"
        highlightColor="var(--color-dark-amethyst-800)"
      >
        <Outlet />
      </SkeletonTheme>
    </ExchangeRateProvider>
  );
}

export function ErrorBoundary(): React.ReactNode {
  return <ErrorView />;
}
