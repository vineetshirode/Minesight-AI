import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  publicDir: false,
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
  },
  build: {
    outDir: resolve(__dirname, '../dashboard/dist'),
    emptyOutDir: true,
    lib: {
      entry: resolve(__dirname, 'src/mountMap.jsx'),
      name: 'MineSightMap',
      fileName: () => 'map-bundle.js',
      formats: ['iife'],
    },
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'map-bundle.css';
          }
          return assetInfo.name || 'asset-[name][extname]';
        },
      },
    },
  },
  server: {
    port: 5173,
    open: false,
  },
});
