import { ApiService } from './api';

/**
 * Tipos para configuración de asistencia
 */
export interface ConfiguracionAsistencia {
  id: number;
  proyecto_id: number;
  modo_asistencia_activo: boolean;
  politica_horas_extras: 'compensar_deuda' | 'bloquear_extras' | 'separar_cuentas';
  tolerancia_retraso_minutos: number;
  marcar_salida_automatica: boolean;
  permitir_justificaciones: boolean;
  requiere_aprobacion_justificaciones: boolean;
  limite_horas_justificables?: number;
  periodo_limite_justificaciones?: 'diario' | 'semanal' | 'mensual' | 'anual';
  enviar_recordatorio_marcado: boolean;
  enviar_alerta_deuda: boolean;
  hora_recordatorio_entrada?: string;
  hora_recordatorio_salida?: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface ActualizarConfiguracionRequest {
  politica_horas_extras?: 'compensar_deuda' | 'bloquear_extras' | 'separar_cuentas';
  tolerancia_retraso_minutos?: number;
  marcar_salida_automatica?: boolean;
  permitir_justificaciones?: boolean;
  requiere_aprobacion_justificaciones?: boolean;
  limite_horas_justificables?: number;
  periodo_limite_justificaciones?: 'diario' | 'semanal' | 'mensual' | 'anual';
  enviar_recordatorio_marcado?: boolean;
  enviar_alerta_deuda?: boolean;
  hora_recordatorio_entrada?: string;
  hora_recordatorio_salida?: string;
}

/**
 * Servicio para gestionar configuración de asistencia
 */
export class ConfiguracionAsistenciaService extends ApiService {
  /**
   * Obtiene la configuración de asistencia de un proyecto
   */
  static async obtenerConfiguracion(proyectoId: number): Promise<ConfiguracionAsistencia> {
    return this.get(`/api/configuracion-asistencia/proyecto/${proyectoId}`);
  }

  /**
   * Actualiza la configuración de asistencia de un proyecto
   */
  static async actualizarConfiguracion(
    proyectoId: number,
    data: ActualizarConfiguracionRequest
  ): Promise<ConfiguracionAsistencia> {
    return this.put(`/api/configuracion-asistencia/proyecto/${proyectoId}`, data);
  }

  /**
   * Activa el modo de asistencia para un proyecto
   */
  static async activarAsistencia(
    proyectoId: number,
    data?: ActualizarConfiguracionRequest
  ): Promise<ConfiguracionAsistencia> {
    return this.post(`/api/configuracion-asistencia/proyecto/${proyectoId}/activar`, data || {});
  }

  /**
   * Desactiva el modo de asistencia para un proyecto
   */
  static async desactivarAsistencia(proyectoId: number): Promise<{ message: string }> {
    return this.post(`/api/configuracion-asistencia/proyecto/${proyectoId}/desactivar`, {});
  }
}
