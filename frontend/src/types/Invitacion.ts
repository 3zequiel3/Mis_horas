export interface Invitacion {
  id: number;
  proyecto_id: number;
  empleado_id: number;
  usuario_existente_id?: number;
  email_destinatario: string;
  mensaje_invitacion?: string;
  token: string;
  estado: 'pendiente' | 'aceptada' | 'rechazada' | 'expirada' | 'cancelada';
  fecha_envio: string;
  fecha_creacion?: string; // Legacy, usar fecha_envio
  fecha_expiracion: string;
  fecha_respuesta?: string;
  intentos_reenvio: number;
  ultima_fecha_reenvio?: string;
  esta_vigente: boolean;
  // Campos agregados desde relaciones
  empleado_nombre?: string;
  proyecto_nombre?: string;
  // Relaciones (legacy)
  proyecto?: {
    id: number;
    nombre: string;
  };
  empleado?: {
    id: number;
    nombre: string;
    apellido?: string;
  };
}

export interface InvitacionResponse {
  success: boolean;
  data: {
    invitacion: Invitacion;
  };
}

export interface InvitacionesResponse {
  success: boolean;
  data: {
    invitaciones: Invitacion[];
  };
}

export interface UsuarioBusqueda {
  id: number;
  username: string;
  email: string;
  nombre_completo?: string;
}

export interface UsuariosBusquedaResponse {
  success: boolean;
  data: {
    usuarios: UsuarioBusqueda[];
  };
}

export interface VerificarEmailResponse {
  success: boolean;
  data: {
    existe: boolean;
    usuario?: UsuarioBusqueda;
  };
}
