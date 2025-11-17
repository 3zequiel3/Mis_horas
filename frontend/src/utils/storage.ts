/**
 * Storage Utilities - Wrapper seguro para localStorage en SSR
 */

/**
 * Obtiene instancia segura de localStorage
 * Retorna null si no está disponible (SSR)
 */
export function getStorage(): Storage | null {
  try {
    return typeof window !== 'undefined' ? window.localStorage : null;
  } catch {
    return null;
  }
}

/**
 * Obtiene un item del storage
 */
export function getStorageItem(key: string): string | null {
  const storage = getStorage();
  return storage ? storage.getItem(key) : null;
}

/**
 * Establece un item en el storage
 */
export function setStorageItem(key: string, value: string): void {
  const storage = getStorage();
  if (storage) {
    storage.setItem(key, value);
  }
}

/**
 * Remueve un item del storage
 */
export function removeStorageItem(key: string): void {
  const storage = getStorage();
  if (storage) {
    storage.removeItem(key);
  }
}

/**
 * Limpia todo el storage
 */
export function clearStorage(): void {
  const storage = getStorage();
  if (storage) {
    storage.clear();
  }
}
