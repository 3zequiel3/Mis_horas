export type TipoNotificacion = 
  | 'invitacion_proyecto'
  | 'invitacion_aceptada'
  | 'invitacion_rechazada'
  | 'justificacion_enviada'
  | 'justificacion_aprobada'
  | 'justificacion_rechazada'
  | 'alerta_deuda'
  | 'recordatorio_marcado'
  | 'alerta_exceso_horario'
  | 'salida_automatica'
  | 'confirmacion_horas_extras'
  | 'sistema';

export interface Notificacion {
  id: number;
  usuario_id: number;
  tipo: TipoNotificacion;
  titulo: string;
  mensaje: string;
  metadata?: Record<string, any>;
  leida: boolean;
  archivada: boolean;
  url_accion?: string;
  fecha_creacion: string;
  fecha_lectura?: string;
}

export interface NotificacionResponse {
  success: boolean;
  data: {
    notificaciones: Notificacion[];
    total: number;
  };
}

export interface ContadorNotificacionesResponse {
  success: boolean;
  data: {
    no_leidas: number;
  };
}
