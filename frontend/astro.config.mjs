import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import dotenv from 'dotenv';
import path from 'path';

// Cargar variables del .env desde la raíz del proyecto (un nivel arriba)
dotenv.config({ path: path.resolve(process.cwd(), '../.env') });

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
    envDir: path.resolve(process.cwd(), '..'),
    define: {
      // Exponer las variables de entorno para el cliente
      'import.meta.env.VITE_API_URL_SERVER': JSON.stringify(process.env.VITE_API_URL_SERVER),
      'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL)
    }
  }
});
