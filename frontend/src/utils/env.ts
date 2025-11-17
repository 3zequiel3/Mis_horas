/**
 * Variables de entorno centralizadas
 * Cargadas desde import.meta.env (variables VITE_*)
 */

// Las variables VITE_* se reemplazan en tiempo de build por Astro
// Si no está disponible, intenta obtener del proceso
let API_URL = '';

// En producción (build time): import.meta.env.VITE_API_URL está disponible
if (typeof import.meta !== 'undefined' && (import.meta.env as any).VITE_API_URL) {
  API_URL = (import.meta.env as any).VITE_API_URL;
}
// En desarrollo: intenta obtener de window.__ENV__
else if (typeof window !== 'undefined' && (window as any).__ENV__?.VITE_API_URL) {
  API_URL = (window as any).__ENV__.VITE_API_URL;
}
// Fallback: intenta obtener del atributo data
else if (typeof document !== 'undefined') {
  const htmlElement = document.documentElement;
  API_URL = htmlElement.getAttribute('data-vite-api-url') || '';
}

// Validar que la variable esté disponible
if (!API_URL) {
  console.error('import.meta.env:', import.meta.env);
  console.warn('Intentando obtener VITE_API_URL del localStorage...');
  API_URL = localStorage.getItem('VITE_API_URL') || '';
}

if (!API_URL) {
  throw new Error(
    'Variable de entorno VITE_API_URL no está disponible.\n' +
    'Por favor, asegúrate de:\n' +
    '1. El archivo .env en la raíz tiene: VITE_API_URL=http://localhost:22000\n' +
    '2. Ejecutaste: docker compose build frontend\n' +
    '3. Ejecutaste: docker compose restart frontend'
  );
}

export const ENV = {
  VITE_API_URL: API_URL,
} as const;
