/**
 * Variables de entorno centralizadas
 * Detecta automáticamente si está en servidor (Astro SSR) o cliente (navegador)
 */

// Detectar si estamos en el servidor (SSR) o cliente
const isServer = typeof window === 'undefined';

// Obtener variables de import.meta.env (Vite)
const { VITE_API_URL_SERVER, VITE_API_URL } = import.meta.env;

// Seleccionar URL según el contexto
const API_URL = isServer ? VITE_API_URL_SERVER : VITE_API_URL;

if (!API_URL) {
  throw new Error(
    'Variable de entorno API_URL no está disponible.\n' +
    'VITE_API_URL_SERVER: ' + (VITE_API_URL_SERVER || 'undefined') + '\n' +
    'VITE_API_URL: ' + (VITE_API_URL || 'undefined')
  );
}

export const ENV = {
  VITE_API_URL: API_URL,
} as const;
