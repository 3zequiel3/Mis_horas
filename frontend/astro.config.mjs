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
    define: {
      // URLs diferentes para SSR (servidor) y cliente
      'import.meta.env.VITE_API_URL_SERVER': JSON.stringify(process.env.VITE_API_URL || 'http://mis_horas_backend:5000'),
      // Usar window.location.hostname para adaptar automáticamente al host actual
      'import.meta.env.VITE_API_URL_CLIENT': JSON.stringify('__DYNAMIC__')
    }
  }
});
