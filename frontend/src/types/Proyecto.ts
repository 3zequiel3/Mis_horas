/**
 * Tipos relacionados con Proyecto
 */

import type { Empleado } from './Empleado';

export interface Proyecto {
  id: number;
  nombre: string;
  descripcion?: string;
  anio: number;
  mes: number;
  usuario_id: number;
  activo: boolean;
  tipo_proyecto: 'personal' | 'empleados';
  horas_reales_activas: boolean;
  empleados?: Empleado[];
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

export interface CreateProyectoRequest {
  nombre: string;
  descripcion?: string;
  anio: number;
  mes: number;
  tipo_proyecto: 'personal' | 'empleados';
  empleados?: string[];
  horas_reales_activas?: boolean;
}

export interface ProyectoView {
  proyecto: Proyecto;
  isActive: boolean;
  statusText: string;
  statusClass: string;
}
