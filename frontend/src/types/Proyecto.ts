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
  tipo_proyecto: 'personal' | 'empleados' | 'colaborativo';
  horas_reales_activas: boolean;
  empleados?: Empleado[];
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  
  // Sistema de turnos
  modo_horarios?: 'corrido' | 'turnos';
  horario_inicio?: string | null;  // Formato HH:MM
  horario_fin?: string | null;     // Formato HH:MM
  turno_manana_inicio?: string | null;  // Formato HH:MM
  turno_manana_fin?: string | null;     // Formato HH:MM
  turno_tarde_inicio?: string | null;   // Formato HH:MM
  turno_tarde_fin?: string | null;      // Formato HH:MM
  
  // Configuración adicional (Fase 4)
  client_name?: string | null;
  brand_color?: string;
  modules_config?: ModulesConfig;
  budget_type?: 'none' | 'hourly_retainer' | 'time_and_materials' | 'fixed_price';
  budget_base_amount?: number | null;
  currency?: string;
  configuracion_asistencia?: ConfiguracionAsistenciaProyecto;
}

export interface ModulesConfig {
  time_tracking: boolean;
  budget: boolean;
  audit: boolean;
  approvals: boolean;
  public_view: boolean;
}

export interface ConfiguracionAsistenciaProyecto {
  modo_horarios: 'corrido' | 'turnos';
  horario_inicio?: string | null;
  horario_fin?: string | null;
  turno_manana_inicio?: string | null;
  turno_manana_fin?: string | null;
  turno_tarde_inicio?: string | null;
  turno_tarde_fin?: string | null;
}

export interface BudgetData {
  budget_type: string;
  budget_base_amount: number | null;
  currency: string;
}

export interface CreateProyectoRequest {
  nombre: string;
  descripcion?: string;
  anio: number;
  mes: number;
  tipo_proyecto: 'personal' | 'empleados' | 'colaborativo';
  empleados?: string[];
  horas_reales_activas?: boolean;
  
  // Sistema de turnos
  modo_horarios?: 'corrido' | 'turnos';
  horario_inicio?: string;
  horario_fin?: string;
  turno_manana_inicio?: string;
  turno_manana_fin?: string;
  turno_tarde_inicio?: string;
  turno_tarde_fin?: string;
}

export interface ProyectoView {
  proyecto: Proyecto;
  isActive: boolean;
  statusText: string;
  statusClass: string;
}
