// ==================== USUARIO ====================
export interface Usuario {
  id: number;
  username: string;
  email: string;
  nombre_completo?: string;
  foto_perfil?: string;
  activo: boolean;
  usar_horas_reales: boolean;
  dia_inicio_semana: number; // 0=Domingo, 1=Lunes
  fecha_creacion: string;
  ultimo_acceso?: string;
}

export interface AuthResponse {
  access_token: string;
  usuario: Usuario;
}

export interface UpdateProfileRequest {
  nombre_completo?: string;
  email?: string;
  foto_perfil?: string;
}

export interface ChangePasswordRequest {
  password_actual: string;
  password_nueva: string;
}

// ==================== PROYECTO ====================
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

// ==================== EMPLEADO ====================
export interface Empleado {
  id: number;
  nombre: string;
  proyecto_id: number;
  activo: boolean;
  fecha_creacion?: string;
}

export interface Estadisticas {
  proyectos_activos: number;
  total_horas: number;
  horas_semana: number;
  promedio_diario: number;
  usando_horas_reales: boolean;
}

// ==================== DÍA ====================
export interface Dia {
  id: number;
  fecha: string;
  dia_semana: string;
  horas_trabajadas: number;
  horas_reales: number;
  hora_entrada?: string | null;  // Formato HH:MM
  hora_salida?: string | null;   // Formato HH:MM
  proyecto_id: number;
  empleado_id?: number;
  creado_en?: string;
  actualizado_en?: string;
}

export interface CreateDiaRequest {
  fecha: string;
  horas_trabajadas: number;
  horas_reales?: number;
  proyecto_id: number;
}

export interface UpdateDiaRequest {
  horas_trabajadas?: number;
  horas_reales?: number;
}

// ==================== TAREA ====================
export interface Tarea {
  id: number;
  titulo: string;
  detalle?: string;
  horas: string;
  que_falta?: string;
  proyecto_id: number;
  dias?: Dia[];
  creado_en?: string;
  actualizado_en?: string;
}

export interface CreateTareaRequest {
  titulo: string;
  detalle?: string;
  horas?: string;
  que_falta?: string;
  proyecto_id: number;
  dias_ids?: number[];
}

export interface UpdateTareaRequest {
  titulo?: string;
  detalle?: string;
  horas?: string;
  que_falta?: string;
}

// ==================== VIEW MODELS ====================
export interface ProyectoView {
  proyecto: Proyecto;
  isActive: boolean;
  statusText: string;
  statusClass: string;
}

export interface TabConfig {
  id: string;
  label: string;
  icon: string;
}

export interface DiaRow {
  dia: Dia;
  horasFormato: string;
  horasRealesFormato: string;
  diaSemana: string;
}

export interface TareaListItem {
  tarea: Tarea;
  diasCount: number;
}

// ==================== API RESPONSES ====================
export interface ErrorResponse {
  error: string;
  detail?: string;
}

export interface SuccessResponse<T> {
  data: T;
  message: string;
}
