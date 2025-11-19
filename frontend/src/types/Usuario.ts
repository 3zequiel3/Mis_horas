/**
 * Tipos relacionados con Usuario
 */

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
