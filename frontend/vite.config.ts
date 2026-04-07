import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === "production" ? "/static/frontend/" : "/",
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: "localhost",
      },
      "/accounts": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: "localhost",
      },
    },
  },
  build: {
    outDir: path.resolve(__dirname, "../static/frontend"),
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: "index.js",
        chunkFileNames: "chunks/[name].js",
        assetFileNames: "assets/[name].[ext]",
      },
    },
  },
}));
