import type { Usuario, UpdateProfileRequest } from '../types';
import { ApiService } from './api';

/**
 * Servicio para gestionar usuarios
 * Extiende ApiService para reutilizar lógica de autenticación
 */
export class UsuarioService extends ApiService {
  /**
   * Obtiene el usuario actual autenticado
   */
  static async getCurrentUser(): Promise<Usuario> {
    return this.get('/api/auth/me');
  }

  /**
   * Obtiene un usuario por ID
   */
  static async getUsuario(usuario_id: number): Promise<Usuario> {
    return this.get(`/api/usuarios/${usuario_id}`);
  }

  /**
   * Actualiza el perfil del usuario
   */
  static async updateProfile(data: UpdateProfileRequest): Promise<Usuario> {
    return this.put('/api/auth/me', data);
  }

  /**
   * Cambia la contraseña del usuario
   */
  static async changePassword(passwordActual: string, passwordNueva: string): Promise<void> {
    await this.post('/api/auth/change-password', {
      password_actual: passwordActual,
      password_nueva: passwordNueva,
    });
  }

  /**
   * Activa o desactiva el uso de horas reales
   */
  static async toggleHorasReales(activar: boolean): Promise<void> {
    await this.post('/api/auth/horas-reales', { activar });
  }
}
