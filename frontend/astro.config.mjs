import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import dotenv from 'dotenv';

// Cargar variables del .env
dotenv.config();

export default defineConfig({
  output: 'server',
  adapter: node({
    mode: 'standalone'
  }),
  server: {
    host: '0.0.0.0',
    port: 3000,
  },
  vite: {
    ssr: {
      external: ['fsevents']
    },
    // Exponer variables VITE_* desde el .env
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL)
    }
  }
});
