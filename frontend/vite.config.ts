import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === 'production' ? '/static/frontend/' : '/',
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/accounts': 'http://localhost:8000'
    }
  },
  build: {
    outDir: path.resolve(__dirname, '../static/frontend'),
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',
        chunkFileNames: 'chunks/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  }
}));
