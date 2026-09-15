import constants, { type RoutePath } from "@constants";
import { asset } from "@utils/asset";
import type { MetaDescriptor } from "react-router";

/*
 * Build the complete head metadata for a route.
 *
 * React Router renders only the deepest route module that exports `meta`, so
 * every route has to emit the full tag set.
 */
export function routeMeta(path: RoutePath): MetaDescriptor[] {
  const { title, description, robots = "index, follow" } = constants.META[path];
  return [
    { title },
    { name: "description", content: description },
    { name: "robots", content: robots },
    { property: "og:title", content: title },
    { property: "og:description", content: description },
    { property: "og:image", content: asset("og.png") },
    { property: "og:image:width", content: "1200" },
    { property: "og:image:height", content: "630" },
    { property: "og:url", content: "https://puckhate.com" },
    { property: "og:type", content: "website" },
    { property: "og:site_name", content: "PUCKHATE!" },
    { name: "twitter:card", content: "summary_large_image" },
    { name: "twitter:title", content: title },
    { name: "twitter:description", content: description },
    { name: "twitter:image", content: asset("og.png") },
  ];
}
