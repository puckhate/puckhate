import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

const proxyTarget = process.env.VITE_PROXY_TARGET || "http://localhost:8000";

// https://vitejs.dev/config/
export default defineConfig(({ command }) => ({
  // Built assets are served by Django + WhiteNoise under /static/; the Vite
  // dev server runs the app at the root.
  base: command === "build" ? "/static/" : "/",
  plugins: [react(), tailwindcss()],
  resolve: {
    tsconfigPaths: true,
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
  },
  build: {
    // Emit the SPA into the Django project so WhiteNoise can serve it.
    outDir: path.resolve(import.meta.dirname, "../backend/spa"),
    emptyOutDir: true,
    sourcemap: "hidden",
  },
}));
