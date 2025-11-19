/**
 * Middleware de Astro - Se ejecuta en TODAS las requests del servidor
 * Maneja autenticación de forma segura antes de renderizar páginas
 */

import { defineMiddleware } from 'astro:middleware';

// Rutas públicas que no requieren autenticación
const PUBLIC_PATHS = [
  '/',
  '/login',
  '/register',
];

// Rutas que solo pueden acceder usuarios NO autenticados
const GUEST_ONLY_PATHS = [
  '/login',
  '/register',
];

/**
 * Verifica si un JWT está expirado
 */
function isJWTExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    
    const payload = JSON.parse(atob(parts[1]));
    if (!payload.exp) return false;
    
    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
  } catch {
    return true;
  }
}

export const onRequest = defineMiddleware(async (context, next) => {
  const { url, cookies, redirect } = context;
  const pathname = url.pathname;

  // Obtener token de autenticación (mismo nombre que usa auth.ts)
  const token = cookies.get('auth_token')?.value;
  
  // Verificar si el token existe y es válido
  const isAuthenticated = token && !isJWTExpired(token);

  // Permitir acceso a assets estáticos
  if (pathname.startsWith('/_astro/') || 
      pathname.startsWith('/favicon') ||
      pathname.endsWith('.css') ||
      pathname.endsWith('.js') ||
      pathname.endsWith('.jpg') ||
      pathname.endsWith('.png') ||
      pathname.endsWith('.svg')) {
    return next();
  }

  // Si la ruta es solo para invitados (login, register) y el usuario está autenticado
  if (GUEST_ONLY_PATHS.includes(pathname) && isAuthenticated) {
    return redirect('/dashboard');
  }

  // Si la ruta es pública, permitir acceso
  if (PUBLIC_PATHS.includes(pathname)) {
    return next();
  }

  // Para todas las demás rutas, requerir autenticación
  if (!isAuthenticated) {
    // Si hay token pero está expirado, limpiarlo
    if (token) {
      cookies.delete('auth_token', { path: '/' });
    }
    return redirect('/login');
  }

  // Usuario autenticado, continuar con la request
  return next();
});
