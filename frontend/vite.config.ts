import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server proxies API calls to the FastAPI backend so the browser
// never makes a cross-origin request (no CORS config needed on the backend).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
