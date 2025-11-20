import { ApiService } from './api';
import type { Notificacion, NotificacionResponse, ContadorNotificacionesResponse } from '../types/Notificacion';

export class NotificacionService extends ApiService {
  /**
   * Obtiene las notificaciones del usuario
   */
  static async obtenerNotificaciones(
    soloNoLeidas: boolean = false,
    limit: number = 50,
    offset: number = 0
  ): Promise<{ notificaciones: Notificacion[]; total: number }> {
    const params = new URLSearchParams({
      solo_no_leidas: soloNoLeidas.toString(),
      limit: limit.toString(),
      offset: offset.toString(),
    });

    const response = await this.get<NotificacionResponse>(`/api/notificaciones?${params}`);
    return response.data;
  }

  /**
   * Obtiene el contador de notificaciones no leídas
   */
  static async obtenerContador(): Promise<number> {
    const response = await this.get<ContadorNotificacionesResponse>('/api/notificaciones/contador');
    return response.data.no_leidas;
  }

  /**
   * Marca una notificación como leída
   */
  static async marcarComoLeida(notificacionId: number): Promise<void> {
    await this.put(`/api/notificaciones/${notificacionId}/marcar-leida`);
  }

  /**
   * Marca todas las notificaciones como leídas
   */
  static async marcarTodasComoLeidas(): Promise<void> {
    await this.put('/api/notificaciones/marcar-todas-leidas');
  }

  /**
   * Archiva una notificación
   */
  static async archivarNotificacion(notificacionId: number): Promise<void> {
    await this.put(`/api/notificaciones/${notificacionId}/archivar`);
  }

  /**
   * Elimina una notificación
   */
  static async eliminarNotificacion(notificacionId: number): Promise<void> {
    await this.delete(`/api/notificaciones/${notificacionId}`);
  }
}
