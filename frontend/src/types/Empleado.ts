/**
 * Tipos relacionados con Empleado
 */

export interface Empleado {
  id: number;
  nombre: string;
  proyecto_id: number;
  activo: boolean;
  fecha_creacion?: string;
}
