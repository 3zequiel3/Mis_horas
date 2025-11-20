import type { AuthResponse, Usuario } from '../types';
import { getStorageItem, setStorageItem, removeStorageItem } from '../utils/storage';
import { getCookie } from '../utils/cookies';
import { ENV } from '../utils/env';

const API_URL = ENV.VITE_API_URL;

// 30 días en segundos
const REMEMBER_ME_DURATION = 30 * 24 * 60 * 60;

// Helper para verificar si estamos en el cliente
const isClient = () => typeof window !== 'undefined';

// Helper para obtener sessionStorage o localStorage
function getStorage(useSession: boolean = false): Storage | null {
  if (!isClient()) return null;
  
  try {
    return useSession ? window.sessionStorage : window.localStorage;
  } catch {
    return null;
  }
}

import { isJWTExpired } from '../utils/jwt';

export class AuthService {
  private static readonly TOKEN_SESSION = 'auth_token_session';  // sessionStorage (se borra con pestaña)
  private static readonly TOKEN_PERSIST = 'auth_token_persist';  // localStorage (persiste 30 días)
  private static readonly USER_STORAGE = 'user';
  private static readonly REMEMBER_ME_FLAG = 'remember_me_enabled';

  static setToken(token: string, rememberMe: boolean = false): void {
    if (!isClient()) return;

    if (rememberMe) {
      // Guardar en localStorage con cookie de 30 días
      const storage = getStorage(false);
      if (storage) {
        storage.setItem(this.TOKEN_PERSIST, token);
        storage.setItem(this.REMEMBER_ME_FLAG, 'true');
      }
      
      // Establecer cookie para que el servidor (middleware) lo valide
      this.setCookie('auth_token', token, {
        maxAge: REMEMBER_ME_DURATION,
        path: '/',
        secure: false, // Cambiar a true en producción con HTTPS
        sameSite: 'Lax',
      });
    } else {
      // Guardar en sessionStorage (se borra automáticamente al cerrar pestaña/navegador)
      const storage = getStorage(true);
      if (storage) {
        storage.setItem(this.TOKEN_SESSION, token);
        storage.removeItem(this.TOKEN_PERSIST);
        storage.removeItem(this.REMEMBER_ME_FLAG);
      }
      
      // IMPORTANTE: También establecer cookie de sesión para el middleware
      // La cookie expira cuando se cierra el navegador (sin maxAge)
      this.setCookie('auth_token', token, {
        path: '/',
        secure: false, // Cambiar a true en producción con HTTPS
        sameSite: 'Lax',
      });
    }
  }

  private static setCookie(name: string, value: string, options?: { maxAge?: number; path?: string; secure?: boolean; sameSite?: string }): void {
    if (!isClient()) return;

    let cookieString = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;

    if (options) {
      if (options.maxAge) {
        cookieString += `; Max-Age=${options.maxAge}`;
      }
      if (options.path) {
        cookieString += `; Path=${options.path}`;
      }
      if (options.secure) {
        cookieString += '; Secure';
      }
      if (options.sameSite) {
        cookieString += `; SameSite=${options.sameSite}`;
      }
    }

    document.cookie = cookieString;
  }

  private static removeCookie(name: string, path: string = '/'): void {
    if (!isClient()) return;
    
    this.setCookie(name, '', {
      maxAge: 0,
      path,
    });
  }

  static getToken(): string | null {
    if (!isClient()) return null;

    // Primero intentar obtener del sessionStorage (sesión actual)
    const sessionStorage = getStorage(true);
    if (sessionStorage) {
      const sessionToken = sessionStorage.getItem(this.TOKEN_SESSION);
      if (sessionToken && !isJWTExpired(sessionToken)) {
        return sessionToken;
      }
    }

    // Luego intentar obtener del localStorage (mantener sesión)
    const localStorage = getStorage(false);
    if (localStorage) {
      const persistToken = localStorage.getItem(this.TOKEN_PERSIST);
      if (persistToken && !isJWTExpired(persistToken)) {
        return persistToken;
      }
    }

    // Si no está en storage, intentar obtener de la cookie
    // Esto permite que funcione en nuevas pestañas cuando no se marcó "remember me"
    const cookieToken = getCookie('auth_token');
    if (cookieToken && !isJWTExpired(cookieToken)) {
      // Restaurar el token al sessionStorage para futuras peticiones en esta pestaña
      const sessionStorage = getStorage(true);
      if (sessionStorage) {
        sessionStorage.setItem(this.TOKEN_SESSION, cookieToken);
      }
      return cookieToken;
    }

    // Si hay token expirado, limpiar
    this.clearToken();
    return null;
  }

  static clearToken(): void {
    if (!isClient()) return;

    // Limpiar sessionStorage
    const sessionStorage = getStorage(true);
    if (sessionStorage) {
      sessionStorage.removeItem(this.TOKEN_SESSION);
    }

    // Limpiar localStorage
    const localStorage = getStorage(false);
    if (localStorage) {
      localStorage.removeItem(this.TOKEN_PERSIST);
      localStorage.removeItem(this.REMEMBER_ME_FLAG);
    }

    // Limpiar usuario
    removeStorageItem(this.USER_STORAGE);

    // IMPORTANTE: Eliminar la cookie para el middleware
    this.removeCookie('auth_token', '/');
  }

  static isAuthenticated(): boolean {
    if (!isClient()) return false;

    const token = this.getToken();
    return !!token && !isJWTExpired(token);
  }

  static async register(
    username: string,
    email: string,
    password: string,
    nombre_completo?: string,
    token_invitacion?: string
  ): Promise<AuthResponse & { proyecto_id?: number }> {
    const body: any = { username, email, password, nombre_completo };
    
    if (token_invitacion) {
      body.token_invitacion = token_invitacion;
    }
    
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error en el registro');
    }

    const data: AuthResponse & { proyecto_id?: number } = await response.json();
    
    // Auto-login: guardar token sin remember_me (sesión temporal)
    this.setToken(data.access_token, false);
    setStorageItem(this.USER_STORAGE, JSON.stringify(data.usuario));

    return data;
  }

  static async login(
    username: string,
    password: string,
    rememberMe: boolean = false
  ): Promise<AuthResponse> {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password, remember_me: rememberMe }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al iniciar sesión');
    }

    const data: AuthResponse = await response.json();
    this.setToken(data.access_token, rememberMe);
    setStorageItem(this.USER_STORAGE, JSON.stringify(data.usuario));

    return data;
  }

  static async getCurrentUser(): Promise<Usuario> {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Error al obtener usuario');
    }

    return response.json();
  }

  static async updateProfile(
    nombre_completo?: string,
    email?: string,
    dia_inicio_semana?: number,
    foto_perfil?: string
  ): Promise<{ usuario: Usuario }> {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      method: 'PUT',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ nombre_completo, email, dia_inicio_semana, foto_perfil }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al actualizar perfil');
    }

    return response.json();
  }

  static async changePassword(
    password_actual: string,
    password_nueva: string
  ): Promise<{ message: string }> {
    const response = await fetch(`${API_URL}/api/auth/change-password`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password_actual, password_nueva }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al cambiar contraseña');
    }

    return response.json();
  }

  static async toggleHorasReales(activar: boolean): Promise<{ message: string }> {
    const response = await fetch(`${API_URL}/api/auth/horas-reales`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ activar }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al cambiar configuración');
    }

    return response.json();
  }

  static async logout(): Promise<void> {
    const token = this.getToken();
    
    if (token) {
      try {
        // Llamar al endpoint del backend para confirmar logout
        await fetch(`${API_URL}/api/auth/logout`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
        });
      } catch (error) {
        // Si falla la llamada al backend, igual limpiamos el cliente
        console.error('Error al llamar logout en backend:', error);
      }
    }
    
    // Limpiar datos locales
    this.clearToken();
  }

  private static getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return {
      Authorization: `Bearer ${token}`,
    };
  }
}
