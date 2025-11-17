/**
 * Middleware de autenticación para páginas protegidas
 * Se ejecuta en el servidor (Astro) antes de renderizar
 */

import { AuthService } from '../services/auth';

/**
 * Verifica si el usuario está autenticado
 * Si no, redirige al login
 * @param redirect Función de redirección de Astro
 * @throws Redirige al login si no está autenticado
 */
export async function requireAuth(astroContext: any): Promise<void> {
  // Verificar autenticación en cliente (localStorage)
  const isAuthenticated = AuthService.isAuthenticated();

  if (!isAuthenticated) {
    return astroContext.redirect('/login');
  }
}

/**
 * Verifica que el usuario NO esté autenticado
 * Si está autenticado, redirige al dashboard
 * @param redirect Función de redirección de Astro
 * @throws Redirige al dashboard si está autenticado
 */
export async function requireGuest(astroContext: any): Promise<void> {
  const isAuthenticated = AuthService.isAuthenticated();

  if (isAuthenticated) {
    return astroContext.redirect('/dashboard');
  }
}
