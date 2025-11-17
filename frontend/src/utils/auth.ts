/**
 * Utilidades de autenticación - Obtener token de AuthService
 */

import { AuthService } from '../services/auth';

/**
 * Obtiene el token JWT desde AuthService (que maneja sessionStorage y localStorage)
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return AuthService.getToken();
}

/**
 * Obtiene los headers de autenticación con el token JWT
 */
export function getAuthHeaders(): Record<string, string> {
  const token = getToken();
  
  if (!token) {
    return {};
  }
  
  return {
    'Authorization': `Bearer ${token}`,
  };
}
