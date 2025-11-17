/**
 * Event Management Utils - Centraliza lógica de eventos reutilizable
 */

/**
 * Tipo de listener de evento
 */
export type EventListener = (detail: any) => void | Promise<void>;

/**
 * Almacena listeners globales
 */
const listeners: Map<string, Set<EventListener>> = new Map();

/**
 * Suscribe a un evento personalizado
 */
export function on(eventName: string, callback: EventListener): void {
  if (!listeners.has(eventName)) {
    listeners.set(eventName, new Set());
  }
  listeners.get(eventName)?.add(callback);
}

/**
 * Desuscribe de un evento personalizado
 */
export function off(eventName: string, callback: EventListener): void {
  listeners.get(eventName)?.delete(callback);
}

/**
 * Emite un evento personalizado
 */
export function emit(eventName: string, detail?: any): void {
  const callbacks = listeners.get(eventName);
  if (callbacks) {
    callbacks.forEach((callback) => {
      try {
        callback(detail);
      } catch (error) {
        console.error(`Error en listener para ${eventName}:`, error);
      }
    });
  }
}

/**
 * Limpia todos los listeners de un evento
 */
export function clearListeners(eventName: string): void {
  listeners.delete(eventName);
}

/**
 * Limpia todos los listeners
 */
export function clearAllListeners(): void {
  listeners.clear();
}

/**
 * Debounce para funciones
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle para funciones
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}
