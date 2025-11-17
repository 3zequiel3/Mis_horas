/**
 * Variables de entorno centralizadas
 * Detecta automáticamente si está en servidor (Astro SSR) o cliente (navegador)
 */

let API_URL = '';

// Detectar si estamos en el servidor (SSR) o cliente
const isServer = typeof window === 'undefined';

if (isServer) {
  // En servidor Astro: usar URL interna de Docker
  API_URL = (import.meta.env as any).VITE_API_URL_SERVER;
} else {
  // En cliente (navegador): construir URL dinámica usando el hostname actual
  const hostname = window.location.hostname;
  API_URL = `http://${hostname}:21050`;
}

if (!API_URL) {
  throw new Error(
    'Variable de entorno API_URL no está disponible.\n' +
    'VITE_API_URL_SERVER: ' + ((import.meta.env as any).VITE_API_URL_SERVER || 'undefined')
  );
}

export const ENV = {
  VITE_API_URL: API_URL,
} as const;
