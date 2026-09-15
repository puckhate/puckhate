import constants, { type RoutePath } from "@constants";
import { asset } from "@utils/asset";
import type { MetaDescriptor } from "react-router";

/*
 * Absolute URL for a route
 */
function absoluteUrl(path: RoutePath): string | null {
  if (path === "*" || !constants.SITE_URL) return null;
  return path === "/"
    ? `${constants.SITE_URL}/`
    : `${constants.SITE_URL}${path}`;
}

/*
 * Absolute URL for a file in the public directory.
 */
function absoluteAsset(file: string): string | null {
  if (!constants.SITE_URL) return null;
  return `${constants.SITE_URL}${asset(file)}`;
}

/*
 * Sitewide schema.org Organization block.
 */
function organizationLd(): MetaDescriptor[] {
  const url = absoluteUrl("/");
  const logo = absoluteAsset("android-chrome-512x512.png");
  if (!url || !logo) return [];
  return [
    {
      "script:ld+json": {
        "@context": "https://schema.org",
        "@type": "Organization",
        name: "PUCKHATE!",
        url,
        logo,
        description: constants.META["/"].description,
        email: constants.EMAIL,
        sameAs: Object.values(constants.SOCIAL),
      },
    },
  ];
}

const OG_IMAGE_ALT =
  "The words 'Every Goal Has a Price' in bold type on a dark background.";

/*
 * Build the complete head metadata for a route.
 *
 * React Router renders only the deepest route module that exports `meta`, so
 * every route has to emit the full tag set.
 */
export function routeMeta(path: RoutePath): MetaDescriptor[] {
  const { title, description, robots = "index, follow" } = constants.META[path];
  const url = absoluteUrl(path);
  const card = absoluteAsset("og.png");
  return [
    { title },
    { name: "description", content: description },
    { name: "robots", content: robots },
    { property: "og:title", content: title },
    { property: "og:description", content: description },
    ...(card
      ? [
          { property: "og:image", content: card },
          { property: "og:image:width", content: "1200" },
          { property: "og:image:height", content: "630" },
          {
            property: "og:image:alt",
            content: OG_IMAGE_ALT,
          },
        ]
      : []),
    ...(url ? [{ property: "og:url", content: url }] : []),
    { property: "og:type", content: "website" },
    { property: "og:locale", content: "en_US" },
    { property: "og:site_name", content: "PUCKHATE!" },
    { name: "twitter:card", content: "summary_large_image" },
    { name: "twitter:title", content: title },
    { name: "twitter:description", content: description },
    ...(card
      ? [
          { name: "twitter:image", content: card },
          { name: "twitter:image:alt", content: OG_IMAGE_ALT },
        ]
      : []),
    ...(url ? [{ tagName: "link" as const, rel: "canonical", href: url }] : []),
    ...organizationLd(),
  ];
}
