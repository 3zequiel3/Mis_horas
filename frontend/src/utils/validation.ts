/**
 * Validation Utils - Centraliza lógica de validaciones
 */

/**
 * Valida que un email sea válido
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Valida que una contraseña sea segura (mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número)
 */
export function isStrongPassword(password: string): boolean {
  return (
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /\d/.test(password)
  );
}

/**
 * Valida que un campo no esté vacío
 */
export function isNotEmpty(value: string): boolean {
  return value.trim().length > 0;
}

/**
 * Valida un formato de horas HH:MM
 */
export function isValidTimeFormat(time: string): boolean {
  const timeRegex = /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/;
  return timeRegex.test(time);
}

/**
 * Valida que un número esté dentro de un rango
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
}

/**
 * Valida que un array no esté vacío
 */
export function isArrayNotEmpty<T>(array: T[]): boolean {
  return Array.isArray(array) && array.length > 0;
}

/**
 * Valida que una fecha sea válida
 */
export function isValidDate(date: string): boolean {
  const parsedDate = new Date(date);
  return parsedDate instanceof Date && !isNaN(parsedDate.getTime());
}

/**
 * Obtiene mensaje de error según tipo de validación
 */
export function getValidationErrorMessage(type: string, value: string = ''): string {
  const messages: Record<string, string> = {
    email: 'Por favor ingresa un email válido',
    password: 'La contraseña debe tener mínimo 8 caracteres, 1 mayúscula, 1 minúscula y 1 número',
    empty: 'Este campo no puede estar vacío',
    time: 'El formato debe ser HH:MM',
    date: 'La fecha ingresada no es válida',
  };

  return messages[type] || 'Valor inválido';
}
