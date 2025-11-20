/**
 * Validation Utils - Validaciones centralizadas con soporte para mensajes
 */

export interface ValidationResult {
  valid: boolean;
  message?: string;
}

// ==================== Validaciones básicas ====================

/**
 * Valida que un campo no esté vacío
 */
export function validateRequired(value: string, fieldName: string = 'Campo'): ValidationResult {
  if (!value || value.trim().length === 0) {
    return { valid: false, message: `${fieldName} es requerido` };
  }
  return { valid: true };
}

/**
 * Valida que un email sea válido
 */
export function validateEmail(email: string): ValidationResult {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, message: 'Email inválido' };
  }
  return { valid: true };
}

/**
 * Valida que las contraseñas coincidan
 */
export function validatePasswordMatch(password: string, passwordConfirm: string): ValidationResult {
  if (password !== passwordConfirm) {
    return { valid: false, message: 'Las contraseñas no coinciden' };
  }
  return { valid: true };
}

/**
 * Valida que una contraseña sea segura (mínimo 8 caracteres)
 */
export function validatePassword(password: string, minLength: number = 8): ValidationResult {
  if (password.length < minLength) {
    return { 
      valid: false, 
      message: `La contraseña debe tener al menos ${minLength} caracteres` 
    };
  }
  return { valid: true };
}

/**
 * Valida que una contraseña sea fuerte (mayúscula, minúscula, número)
 */
export function validateStrongPassword(password: string): ValidationResult {
  if (password.length < 8) {
    return { valid: false, message: 'La contraseña debe tener al menos 8 caracteres' };
  }
  if (!/[A-Z]/.test(password)) {
    return { valid: false, message: 'La contraseña debe contener al menos una mayúscula' };
  }
  if (!/[a-z]/.test(password)) {
    return { valid: false, message: 'La contraseña debe contener al menos una minúscula' };
  }
  if (!/\d/.test(password)) {
    return { valid: false, message: 'La contraseña debe contener al menos un número' };
  }
  return { valid: true };
}

/**
 * Valida la longitud mínima de un string
 */
export function validateMinLength(value: string, minLength: number, fieldName: string = 'Campo'): ValidationResult {
  if (value.length < minLength) {
    return { valid: false, message: `${fieldName} debe tener al menos ${minLength} caracteres` };
  }
  return { valid: true };
}

// ==================== Validaciones de formato ====================

/**
 * Valida un formato de horas HH:MM
 */
export function validateTimeFormat(time: string): ValidationResult {
  const timeRegex = /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/;
  if (!timeRegex.test(time)) {
    return { valid: false, message: 'El formato debe ser HH:MM' };
  }
  return { valid: true };
}

/**
 * Valida que una fecha sea válida
 */
export function validateDate(date: string): ValidationResult {
  const parsedDate = new Date(date);
  if (!(parsedDate instanceof Date) || isNaN(parsedDate.getTime())) {
    return { valid: false, message: 'La fecha ingresada no es válida' };
  }
  return { valid: true };
}

// ==================== Validaciones numéricas ====================

/**
 * Valida que un número esté dentro de un rango
 */
export function validateRange(value: number, min: number, max: number, fieldName: string = 'Campo'): ValidationResult {
  if (value < min || value > max) {
    return { valid: false, message: `${fieldName} debe estar entre ${min} y ${max}` };
  }
  return { valid: true };
}

/**
 * Valida que un número sea entero
 */
export function validateInteger(value: string | number): ValidationResult {
  const num = typeof value === 'string' ? parseInt(value, 10) : value;
  if (isNaN(num) || !Number.isInteger(num)) {
    return { valid: false, message: 'Debe ser un número entero' };
  }
  return { valid: true };
}

/**
 * Valida que un número sea positivo
 */
export function validatePositive(value: number | string, fieldName: string = 'Campo'): ValidationResult {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num) || num <= 0) {
    return { valid: false, message: `${fieldName} debe ser positivo` };
  }
  return { valid: true };
}

// ==================== Validaciones de arrays ====================

/**
 * Valida que un array no esté vacío
 */
export function validateArrayNotEmpty<T>(array: T[], fieldName: string = 'Lista'): ValidationResult {
  if (!Array.isArray(array) || array.length === 0) {
    return { valid: false, message: `${fieldName} no puede estar vacía` };
  }
  return { valid: true };
}

// ==================== Validaciones de archivos ====================

/**
 * Valida que un archivo tenga una extensión permitida
 */
export function validateFileExtension(filename: string, allowedExtensions: string[]): ValidationResult {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  if (!allowedExtensions.includes(ext)) {
    return {
      valid: false,
      message: `Extensión de archivo no permitida. Use: ${allowedExtensions.join(', ')}`,
    };
  }
  return { valid: true };
}

// ==================== Funciones auxiliares ====================

/**
 * Ejecuta múltiples validaciones y retorna el primer error encontrado
 */
export function validateAll(...validations: ValidationResult[]): ValidationResult {
  for (const validation of validations) {
    if (!validation.valid) {
      return validation;
    }
  }
  return { valid: true };
}

/**
 * Funciones de conveniencia para chequeos rápidos (retornan boolean)
 */
export const is = {
  email: (email: string): boolean => validateEmail(email).valid,
  empty: (value: string): boolean => !validateRequired(value).valid,
  notEmpty: (value: string): boolean => validateRequired(value).valid,
  validTime: (time: string): boolean => validateTimeFormat(time).valid,
  validDate: (date: string): boolean => validateDate(date).valid,
  inRange: (value: number, min: number, max: number): boolean => validateRange(value, min, max).valid,
  arrayNotEmpty: <T>(array: T[]): boolean => validateArrayNotEmpty(array).valid,
};
