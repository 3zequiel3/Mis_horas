/**
 * Validation Utilities - Validaciones comunes con mensajes claros
 */

export interface ValidationResult {
  valid: boolean;
  message?: string;
}

/**
 * Valida que un campo no esté vacío
 */
export function validateRequired(value: string, fieldName: string = 'Campo'): ValidationResult {
  if (!value || value.trim().length === 0) {
    return {
      valid: false,
      message: `${fieldName} es requerido`,
    };
  }
  return { valid: true };
}

/**
 * Valida un email
 */
export function validateEmail(email: string): ValidationResult {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return {
      valid: false,
      message: 'Email inválido',
    };
  }
  return { valid: true };
}

/**
 * Valida la longitud mínima de un string
 */
export function validateMinLength(
  value: string,
  minLength: number,
  fieldName: string = 'Campo'
): ValidationResult {
  if (value.length < minLength) {
    return {
      valid: false,
      message: `${fieldName} debe tener al menos ${minLength} caracteres`,
    };
  }
  return { valid: true };
}

/**
 * Valida que dos valores coincidan
 */
export function validateMatch(
  value1: string,
  value2: string,
  fieldName: string = 'Campos'
): ValidationResult {
  if (value1 !== value2) {
    return {
      valid: false,
      message: `${fieldName} no coinciden`,
    };
  }
  return { valid: true };
}

/**
 * Valida que un número esté en un rango
 */
export function validateRange(
  value: number,
  min: number,
  max: number,
  fieldName: string = 'Campo'
): ValidationResult {
  if (value < min || value > max) {
    return {
      valid: false,
      message: `${fieldName} debe estar entre ${min} y ${max}`,
    };
  }
  return { valid: true };
}

/**
 * Ejecuta múltiples validaciones
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
 * Valida que un archivo tenga una extensión permitida
 */
export function validateFileExtension(
  filename: string,
  allowedExtensions: string[]
): ValidationResult {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  if (!allowedExtensions.includes(ext)) {
    return {
      valid: false,
      message: `Extensión de archivo no permitida. Use: ${allowedExtensions.join(', ')}`,
    };
  }
  return { valid: true };
}

/**
 * Valida que un número sea entero
 */
export function validateInteger(value: string | number): ValidationResult {
  const num = typeof value === 'string' ? parseInt(value, 10) : value;
  if (isNaN(num) || !Number.isInteger(num)) {
    return {
      valid: false,
      message: 'Debe ser un número entero',
    };
  }
  return { valid: true };
}

/**
 * Valida que un número sea positivo
 */
export function validatePositive(value: number | string, fieldName: string = 'Campo'): ValidationResult {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num) || num <= 0) {
    return {
      valid: false,
      message: `${fieldName} debe ser positivo`,
    };
  }
  return { valid: true };
}
