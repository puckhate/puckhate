import { StrictMode } from "react";

import { ExchangeRateProvider } from "@providers/ExchangeRateProvider";
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

const DESCRIPTION =
  "Every goal #77 Britta Curl-Salemme scores becomes a donation to support the trans community.";

// Asset file path depends on the Vite base URL - /static/ in a build, / in dev
const asset = (file: string) => `${import.meta.env.BASE_URL}${file}`;

export const meta: MetaFunction = () => [
  { title: "PUCKHATE!" },
  { name: "description", content: DESCRIPTION },
  { name: "robots", content: "index, follow" },
  { property: "og:title", content: "PUCKHATE!" },
  { property: "og:description", content: DESCRIPTION },
  { property: "og:image", content: asset("og.png") },
  { property: "og:image:width", content: "1200" },
  { property: "og:image:height", content: "630" },
  { property: "og:url", content: "https://puckhate.com" },
  { property: "og:type", content: "website" },
  { property: "og:site_name", content: "PUCKHATE!" },
  { name: "twitter:card", content: "summary_large_image" },
  { name: "twitter:title", content: "PUCKHATE!" },
  { name: "twitter:description", content: DESCRIPTION },
  { name: "twitter:image", content: asset("og.png") },
];

export const links: LinksFunction = () => [
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
