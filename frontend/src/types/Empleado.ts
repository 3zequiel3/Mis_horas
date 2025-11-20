/**
 * Tipos relacionados con Empleado
 */

export interface Empleado {
  id: number;
  nombre: string;
  apellido?: string; // Campo legacy, mantener por compatibilidad con código existente
  proyecto_id: number;
  activo: boolean;
  usuario_id?: number;
  estado_asistencia?: 'activo' | 'inactivo' | 'suspendido';
  horario_especial_inicio?: string;
  horario_especial_fin?: string;
  usa_horario_especial?: boolean;
  fecha_creacion?: string;
  usuario?: {
    id: number;
    username: string;
    email: string;
    nombre_completo?: string;
  };
}
