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

/**
 * Verifica si el usuario está autenticado y retorna los datos del usuario
 */
export async function verificarAutenticacion(): Promise<any | null> {
  if (typeof window === 'undefined') return null;
  
  const token = getToken();
  if (!token) return null;
  
  const usuarioStr = sessionStorage.getItem('usuario') || localStorage.getItem('usuario');
  if (!usuarioStr) return null;
  
  try {
    return JSON.parse(usuarioStr);
  } catch (error) {
    console.error('Error parsing usuario:', error);
    return null;
  }
}
