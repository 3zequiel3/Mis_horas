/**
 * Tipos relacionados con Configuración de Asistencia
 */

export type PoliticaHorasExtras = 'compensar_deuda' | 'bloquear_extras' | 'separar_cuentas';
export type PeriodoLimite = 'diario' | 'semanal' | 'mensual' | 'anual';

export interface ConfiguracionAsistencia {
  id: number;
  proyecto_id: number;
  modo_asistencia_activo: boolean;
  politica_horas_extras: PoliticaHorasExtras;
  tolerancia_retraso_minutos: number;
  marcar_salida_automatica: boolean;
  permitir_justificaciones: boolean;
  requiere_aprobacion_justificaciones: boolean;
  limite_horas_justificables?: number;
  periodo_limite_justificaciones?: PeriodoLimite;
  enviar_recordatorio_marcado: boolean;
  enviar_alerta_deuda: boolean;
  hora_recordatorio_entrada?: string;
  hora_recordatorio_salida?: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface ActualizarConfiguracionRequest {
  politica_horas_extras?: PoliticaHorasExtras;
  tolerancia_retraso_minutos?: number;
  marcar_salida_automatica?: boolean;
  permitir_justificaciones?: boolean;
  requiere_aprobacion_justificaciones?: boolean;
  limite_horas_justificables?: number;
  periodo_limite_justificaciones?: PeriodoLimite;
  enviar_recordatorio_marcado?: boolean;
  enviar_alerta_deuda?: boolean;
  hora_recordatorio_entrada?: string;
  hora_recordatorio_salida?: string;
}
