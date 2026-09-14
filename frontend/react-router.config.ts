import fs from "node:fs/promises";
import path from "node:path";
import type { Config } from "@react-router/dev/config";

// Django serves the client build from here via whitenoise
const DJANGO_SPA_DIR = path.resolve(
  import.meta.dirname,
  "../backend/spa/client",
);

/** Collect every prerendered `index.html` as a site-absolute route path. */
async function prerenderedRoutes(dir: string, prefix = ""): Promise<string[]> {
  const routes: string[] = [];
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (entry.name === "assets") continue;
      routes.push(
        ...(await prerenderedRoutes(
          path.join(dir, entry.name),
          `${prefix}/${entry.name}`,
        )),
      );
    } else if (entry.name === "index.html") {
      routes.push(prefix === "" ? "/" : prefix);
    }
  }
  return routes.sort();
}

export default {
  appDirectory: "src",
  ssr: false,
  prerender: ({ getStaticPaths }) => getStaticPaths(),

  async buildEnd({ reactRouterConfig }) {
    // Copy finished build to clean Django SPA directory
    const clientDir = path.join(reactRouterConfig.buildDirectory, "client");
    await fs.rm(DJANGO_SPA_DIR, { recursive: true, force: true });
    await fs.cp(clientDir, DJANGO_SPA_DIR, { recursive: true });

    // Generate list of rendered routes for Django (to serve sitemap.xml)
    const routes = await prerenderedRoutes(DJANGO_SPA_DIR);
    await fs.writeFile(
      path.join(DJANGO_SPA_DIR, "routes.json"),
      `${JSON.stringify(routes, null, 2)}\n`,
    );
  },
} satisfies Config;
