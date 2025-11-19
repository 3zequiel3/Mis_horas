/**
 * Utilidades para manejo y formateo de fechas
 */

import { MESES_ES } from './formatters';

/**
 * Formatea una fecha en formato español: "DD/MM/YYYY"
 */
export function formatearFechaCorta(fecha: string | Date): string {
  const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
  
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
}

/**
 * Formatea una fecha en formato corto sin año: "DD/MM"
 */
export function formatearFechaSinAnio(fecha: string | Date): string {
  const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
  
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit'
  });
}

/**
 * Formatea una fecha en formato largo: "1 de enero de 2024"
 */
export function formatearFechaLarga(fecha: string | Date): string {
  const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
  const dia = date.getDate();
  const mes = MESES_ES[(date.getMonth() + 1) as keyof typeof MESES_ES];
  const año = date.getFullYear();
  
  return `${dia} de ${mes} de ${año}`;
}

/**
 * Formatea una fecha con día de la semana corto: "lun, 01/12"
 */
export function formatearFechaConDia(fecha: string | Date): string {
  const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
  
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    weekday: 'short',
  });
}

/**
 * Formatea una fecha con día de la semana y año corto: "lun, 01/12/24"
 */
export function formatearFechaConDiaYAnio(fecha: string | Date): string {
  const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
  
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    weekday: 'short',
  });
}

/**
 * Formatea una fecha de forma segura (maneja valores null/undefined)
 */
export function formatearFechaSegura(dateString?: string | null): string {
  if (!dateString) return '-';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '-';
    return formatearFechaCorta(date);
  } catch {
    return '-';
  }
}

/**
 * Obtiene el nombre del día de la semana
 */
export function obtenerNombreDia(fecha: string | Date): string {
  const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
  
  return date.toLocaleDateString('es-ES', { weekday: 'long' });
}

/**
 * Verifica si una fecha es válida
 */
export function esFechaValida(fecha: string | Date): boolean {
  const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
  return !isNaN(date.getTime());
}

/**
 * Obtiene la fecha actual en formato YYYY-MM-DD
 */
export function obtenerFechaHoy(): string {
  return new Date().toISOString().split('T')[0];
}

/**
 * Compara dos fechas (retorna -1 si fecha1 < fecha2, 0 si son iguales, 1 si fecha1 > fecha2)
 */
export function compararFechas(fecha1: string | Date, fecha2: string | Date): number {
  const d1 = typeof fecha1 === 'string' ? new Date(fecha1) : fecha1;
  const d2 = typeof fecha2 === 'string' ? new Date(fecha2) : fecha2;
  
  if (d1 < d2) return -1;
  if (d1 > d2) return 1;
  return 0;
}
