import { ApiService } from './api';
import type {
  Invitacion,
  InvitacionResponse,
  InvitacionesResponse,
  UsuarioBusqueda,
  UsuariosBusquedaResponse,
  VerificarEmailResponse,
} from '../types/Invitacion';

export class InvitacionService extends ApiService {
  /**
   * Busca usuarios en el sistema
   */
  static async buscarUsuarios(query: string, limit: number = 10): Promise<UsuarioBusqueda[]> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });

    const response = await this.get<UsuariosBusquedaResponse>(`/api/invitaciones/buscar-usuarios?${params}`);
    return response.data.usuarios;
  }

  /**
   * Verifica si un email existe en el sistema y si hay invitaciones previas
   */
  static async verificarEmail(email: string, empleadoId?: number): Promise<{ 
    existe: boolean; 
    usuario?: UsuarioBusqueda;
    invitacion_previa?: Invitacion;
    puede_reenviar?: boolean;
  }> {
    const response = await this.post<any>('/api/invitaciones/verificar-email', { 
      email,
      empleado_id: empleadoId 
    });
    return response.data;
  }

  /**
   * Envía una invitación a un empleado
   */
  static async enviarInvitacion(
    proyectoId: number,
    empleadoId: number,
    emailDestinatario: string,
    mensajeInvitacion?: string
  ): Promise<Invitacion> {
    const response = await this.post<InvitacionResponse>('/api/invitaciones/enviar', {
      proyecto_id: proyectoId,
      empleado_id: empleadoId,
      email_destinatario: emailDestinatario,
      mensaje_invitacion: mensajeInvitacion,
    });
    return response.data.invitacion;
  }

  /**
   * Obtiene las invitaciones del usuario actual
   */
  static async obtenerMisInvitaciones(incluirExpiradas: boolean = false): Promise<Invitacion[]> {
    const params = new URLSearchParams({
      incluir_expiradas: incluirExpiradas.toString(),
    });

    const response = await this.get<InvitacionesResponse>(`/api/invitaciones/mis-invitaciones?${params}`);
    return response.data.invitaciones;
  }

  /**
   * Acepta una invitación
   */
  static async aceptarInvitacion(token: string): Promise<Invitacion> {
    const response = await this.post<InvitacionResponse>(`/api/invitaciones/${token}/aceptar`);
    return response.data.invitacion;
  }

  /**
   * Rechaza una invitación
   */
  static async rechazarInvitacion(token: string, motivo?: string): Promise<Invitacion> {
    const response = await this.post<InvitacionResponse>(`/api/invitaciones/${token}/rechazar`, { motivo });
    return response.data.invitacion;
  }

  /**
   * Reenvía una invitación
   */
  static async reenviarInvitacion(invitacionId: number): Promise<Invitacion> {
    const response = await this.post<InvitacionResponse>(`/api/invitaciones/${invitacionId}/reenviar`);
    return response.data.invitacion;
  }

  /**
   * Obtiene las invitaciones de un proyecto (solo admin)
   */
  static async obtenerInvitacionesProyecto(proyectoId: number): Promise<Invitacion[]> {
    const response = await this.get<InvitacionesResponse>(`/api/invitaciones/proyecto/${proyectoId}`);
    return response.data.invitaciones;
  }

  /**
   * Valida un token de invitación y obtiene sus datos
   */
  static async validarToken(token: string): Promise<Invitacion & { proyecto_nombre?: string }> {
    const response = await this.get<InvitacionResponse>(`/api/invitaciones/validar/${token}`);
    return response.data.invitacion;
  }
}
