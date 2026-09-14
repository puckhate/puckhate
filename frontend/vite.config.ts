import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

const proxyTarget = process.env.VITE_PROXY_TARGET || "http://localhost:8000";

// https://vitejs.dev/config/
export default defineConfig(({ command }) => ({
  // Built assets are served by Django + WhiteNoise under /static/; the dev server under /
  base: command === "build" ? "/static/" : "/",
  plugins: [tailwindcss(), reactRouter()],
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
    sourcemap: "hidden",
  },
}));
