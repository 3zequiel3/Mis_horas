/**
 * Tipos relacionados con Día
 */

export interface Dia {
  id: number;
  fecha: string;
  dia_semana: string;
  horas_trabajadas: number;
  horas_reales: number;
  hora_entrada?: string | null;  // Formato HH:MM (modo corrido)
  hora_salida?: string | null;   // Formato HH:MM (modo corrido)
  
  // Sistema de turnos
  turno?: string | null;  // 'mañana' | 'tarde' | null
  turno_manana_entrada?: string | null;  // Formato HH:MM
  turno_manana_salida?: string | null;   // Formato HH:MM
  turno_tarde_entrada?: string | null;   // Formato HH:MM
  turno_tarde_salida?: string | null;    // Formato HH:MM
  horas_extras?: number;
  observaciones?: string | null;  // Notas adicionales del día
  
  proyecto_id: number;
  empleado_id?: number;
  creado_en?: string;
  actualizado_en?: string;
}

export interface CreateDiaRequest {
  fecha: string;
  horas_trabajadas: number;
  horas_reales?: number;
  proyecto_id: number;
}

export interface UpdateDiaRequest {
  horas_trabajadas?: number;
  horas_reales?: number;
}

export interface DiaRow {
  dia: Dia;
  horasFormato: string;
  horasRealesFormato: string;
  diaSemana: string;
}
