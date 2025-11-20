/**
 * Tipos relacionados con Asistencia y Marcados
 */

export type TipoTurno = 'manana' | 'tarde' | 'nocturno' | 'especial';

export interface MarcadoAsistencia {
  id: number;
  empleado_id: number;
  proyecto_id: number;
  dia_id?: number;
  fecha: string; // ISO date
  turno?: TipoTurno;
  hora_entrada?: string; // HH:MM:SS
  hora_salida?: string; // HH:MM:SS
  entrada_marcada_manualmente: boolean;
  salida_marcada_manualmente: boolean;
  salida_marcada_automaticamente: boolean;
  confirmacion_continua: boolean;
  confirmada_por_admin: boolean;
  horas_trabajadas: number;
  horas_extras: number;
  horas_normales: number;
  observaciones?: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface MarcarEntradaRequest {
  empleado_id: number;
  proyecto_id: number;
  fecha?: string; // ISO date, opcional (default: hoy)
  hora_entrada?: string; // HH:MM:SS, opcional (default: ahora)
  latitud?: number;
  longitud?: number;
}

export interface MarcarSalidaRequest {
  empleado_id: number;
  proyecto_id: number;
  fecha?: string; // ISO date, opcional (default: hoy)
  hora_salida?: string; // HH:MM:SS, opcional (default: ahora)
  latitud?: number;
  longitud?: number;
  confirmacion_continua?: boolean;
}

export interface EditarMarcadoRequest {
  hora_entrada?: string; // HH:MM:SS
  hora_salida?: string; // HH:MM:SS
  observaciones?: string;
}

export interface EstadoHoyResponse {
  tiene_entrada: boolean;
  tiene_salida: boolean;
  marcado?: MarcadoAsistencia;
  horario_proyecto?: {
    modo_horarios: string;
    horario_inicio?: string;
    horario_fin?: string;
  };
}

export interface ObtenerMarcadosParams {
  proyecto_id?: number;
  empleado_id?: number;
  fecha_inicio?: string; // ISO date
  fecha_fin?: string; // ISO date
  turno?: TipoTurno;
}

export interface DetectarAusenciasRequest {
  proyecto_id: number;
  fecha: string; // ISO date
}
