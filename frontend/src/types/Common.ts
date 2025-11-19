/**
 * Tipos comunes y genéricos
 */

export interface ErrorResponse {
  error: string;
  detail?: string;
}

export interface SuccessResponse<T> {
  data: T;
  message: string;
}

export interface Estadisticas {
  proyectos_activos: number;
  total_horas: number;
  horas_semana: number;
  promedio_diario: number;
  usando_horas_reales: boolean;
}

export interface TabConfig {
  id: string;
  label: string;
  icon: string;
}
