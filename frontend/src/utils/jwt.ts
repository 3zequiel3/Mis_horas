/**
 * JWT utilities para manejo de tokens en el frontend
 * Validación de tokens sin verificación de firma (ya que se confía en el servidor)
 */

export interface JWTPayload {
  identity: string;
  iat: number;
  exp: number;
  [key: string]: any;
}

/**
 * Decodifica un JWT sin validar la firma
 * @param token Token JWT
 * @returns Payload decodificado o null si es inválido
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('Token JWT inválido: estructura incorrecta');
      return null;
    }

    const payload = JSON.parse(atob(parts[1]));
    return payload;
  } catch (error) {
    console.error('Error al decodificar JWT:', error);
    return null;
  }
}

/**
 * Verifica si un token JWT ha expirado
 * @param token Token JWT
 * @returns true si ha expirado, false si aún es válido
 */
export function isJWTExpired(token: string): boolean {
  const payload = decodeJWT(token);
  if (!payload) return true;

  // Comparar tiempo de expiración con el tiempo actual
  const now = Math.floor(Date.now() / 1000);
  const isExpired = payload.exp <= now;

  if (isExpired) {
    console.debug('Token expirado:', {
      expiredAt: new Date(payload.exp * 1000),
      now: new Date(now * 1000),
    });
  }

  return isExpired;
}

/**
 * Obtiene el tiempo restante antes de que el token expire
 * @param token Token JWT
 * @returns Tiempo en milisegundos hasta la expiración, o -1 si es inválido/expirado
 */
export function getTokenTimeRemaining(token: string): number {
  const payload = decodeJWT(token);
  if (!payload) return -1;

  const now = Math.floor(Date.now() / 1000);
  const remaining = (payload.exp - now) * 1000;

  return remaining > 0 ? remaining : -1;
}

/**
 * Obtiene información del usuario desde el token
 * @param token Token JWT
 * @returns ID del usuario o null
 */
export function getUserIdFromToken(token: string): string | null {
  const payload = decodeJWT(token);
  return payload?.identity || null;
}

/**
 * Valida completamente un token
 * @param token Token JWT
 * @returns true si el token es válido, false si no
 */
export function isValidJWT(token: string): boolean {
  if (!token || typeof token !== 'string') return false;
  if (isJWTExpired(token)) return false;

  const payload = decodeJWT(token);
  return payload !== null;
}
