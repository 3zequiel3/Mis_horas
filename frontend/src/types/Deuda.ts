/**
 * Tipos relacionados con Deudas de Horas y Justificaciones
 */

export type EstadoDeuda = 'activa' | 'justificada' | 'compensada' | 'cerrada';
export type MotivoDeuda = 'ausencia' | 'salida_temprana' | 'entrada_tardia' | 'otro';

export interface DeudaHoras {
  id: number;
  empleado_id: number;
  proyecto_id: number;
  fecha_inicio: string;
  fecha_fin?: string;
  horas_debidas: number;
  horas_justificadas: number;
  horas_compensadas: number;
  horas_pendientes: number;
  estado: EstadoDeuda;
  motivo: MotivoDeuda;
  descripcion_automatica?: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
  empleado?: {
    id: number;
    nombre: string;
  };
}

export type EstadoJustificacion = 'pendiente' | 'aprobada' | 'rechazada';

export interface Justificacion {
  id: number;
  deuda_id: number;
  empleado_id: number;
  proyecto_id: number;
  motivo: string;
  horas_a_justificar: number;
  archivo_url?: string;
  archivo_nombre?: string;
  archivo_tipo?: string;
  archivo_tamano?: number;
  estado: EstadoJustificacion;
  revisada_por_usuario_id?: number;
  fecha_revision?: string;
  comentario_admin?: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface JustificarDeudaRequest {
  motivo: string;
  horas_a_justificar: number;
  archivo_url?: string;
  archivo_nombre?: string;
  archivo_tipo?: string;
}
