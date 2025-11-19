/**
 * Utilidades para cálculo y manejo de horas
 */

import type { Dia, Usuario, Tarea } from '../types';
import { horasAFormato } from './formatters';

/**
 * Determina si debe mostrar horas reales según la configuración del usuario
 */
export function debeUsarHorasReales(usuario: Usuario | null): boolean {
  return usuario?.usar_horas_reales ?? false;
}

/**
 * Obtiene las horas a mostrar de un día según configuración del usuario
 */
export function obtenerHorasAMostrar(dia: Dia, usarHorasReales: boolean): number {
  return usarHorasReales ? (dia.horas_reales || 0) : (dia.horas_trabajadas || 0);
}

/**
 * Calcula las horas totales de una tarea según los días asignados
 */
export function calcularHorasTarea(tarea: Tarea, usarHorasReales: boolean): string {
  if (!tarea.dias || tarea.dias.length === 0) {
    return '00:00';
  }

  let totalHoras = 0;

  tarea.dias.forEach((dia: Dia) => {
    totalHoras += obtenerHorasAMostrar(dia, usarHorasReales);
  });

  return horasAFormato(totalHoras);
}

/**
 * Calcula el total de horas de un array de días
 */
export function calcularTotalHoras(dias: Dia[], usarHorasReales: boolean): number {
  return dias.reduce((total, dia) => {
    return total + obtenerHorasAMostrar(dia, usarHorasReales);
  }, 0);
}

/**
 * Valida que un valor de horas no sea vacío o cero
 */
export function tieneHorasValidas(horas: number | string): boolean {
  if (typeof horas === 'number') {
    return horas > 0;
  }
  
  const horasStr = horas.trim();
  return horasStr !== '' && horasStr !== '00:00' && horasStr !== '0:00' && horasStr !== '0';
}

/**
 * Calcula las horas entre hora de entrada y salida
 */
export function calcularHorasEntradaSalida(
  horaEntrada: string | null | undefined,
  horaSalida: string | null | undefined
): number {
  if (!horaEntrada || !horaSalida) return 0;
  
  try {
    const [horasEntrada, minutosEntrada] = horaEntrada.split(':').map(Number);
    const [horasSalida, minutosSalida] = horaSalida.split(':').map(Number);
    
    const totalMinutosEntrada = horasEntrada * 60 + minutosEntrada;
    const totalMinutosSalida = horasSalida * 60 + minutosSalida;
    
    const diferenciaMinutos = totalMinutosSalida - totalMinutosEntrada;
    
    return diferenciaMinutos / 60;
  } catch {
    return 0;
  }
}
