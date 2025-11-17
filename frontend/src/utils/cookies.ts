/**
 * Utilidades para manejo de cookies
 */

export interface CookieOptions {
  maxAge?: number; // Segundos
  path?: string;
  domain?: string;
  secure?: boolean;
  sameSite?: 'Strict' | 'Lax' | 'None';
}

/**
 * Establece una cookie
 * @param name Nombre de la cookie
 * @param value Valor de la cookie
 * @param options Opciones de la cookie
 */
export function setCookie(name: string, value: string, options?: CookieOptions): void {
  let cookieString = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;

  if (options) {
    if (options.maxAge) {
      cookieString += `; Max-Age=${options.maxAge}`;
    }
    if (options.path) {
      cookieString += `; Path=${options.path}`;
    }
    if (options.domain) {
      cookieString += `; Domain=${options.domain}`;
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

/**
 * Obtiene el valor de una cookie
 * @param name Nombre de la cookie
 * @returns Valor de la cookie o null
 */
export function getCookie(name: string): string | null {
  const nameEQ = encodeURIComponent(name) + '=';
  const cookies = document.cookie.split(';');

  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.indexOf(nameEQ) === 0) {
      return decodeURIComponent(cookie.substring(nameEQ.length));
    }
  }

  return null;
}

/**
 * Elimina una cookie
 * @param name Nombre de la cookie
 * @param path Path de la cookie
 */
export function removeCookie(name: string, path: string = '/'): void {
  setCookie(name, '', {
    maxAge: 0,
    path,
  });
}

/**
 * Obtiene todas las cookies como un objeto
 */
export function getAllCookies(): Record<string, string> {
  const cookies: Record<string, string> = {};
  const cookieArray = document.cookie.split(';');

  for (let cookie of cookieArray) {
    cookie = cookie.trim();
    const [name, value] = cookie.split('=');

    if (name) {
      cookies[decodeURIComponent(name)] = decodeURIComponent(value || '');
    }
  }

  return cookies;
}

/**
 * Limpia todas las cookies
 */
export function clearAllCookies(): void {
  const cookies = getAllCookies();
  for (const name of Object.keys(cookies)) {
    removeCookie(name);
  }
}
