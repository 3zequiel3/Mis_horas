/**
 * Archivo central de tipos - Re-exporta todos los tipos del proyecto
 * Los tipos están organizados en archivos separados por dominio
 */

// Usuario
export type {
  Usuario,
  AuthResponse,
  UpdateProfileRequest,
  ChangePasswordRequest
} from './Usuario';

// Proyecto
export type {
  Proyecto,
  CreateProyectoRequest,
  ProyectoView
} from './Proyecto';

// Empleado
export type { Empleado } from './Empleado';

// Día
export type {
  Dia,
  CreateDiaRequest,
  UpdateDiaRequest,
  DiaRow
} from './Dia';

// Tarea
export type {
  Tarea,
  CreateTareaRequest,
  UpdateTareaRequest,
  TareaListItem
} from './Tarea';

// Notificaciones
export type {
  Notificacion,
  TipoNotificacion,
  NotificacionResponse,
  ContadorNotificacionesResponse
} from './Notificacion';

// Invitaciones
export type {
  Invitacion,
  InvitacionResponse,
  InvitacionesResponse,
  UsuarioBusqueda,
  UsuariosBusquedaResponse,
  VerificarEmailResponse
} from './Invitacion';

// Comunes
export type {
  ErrorResponse,
  SuccessResponse,
  Estadisticas,
  TabConfig
} from './Common';

// Asistencia
export type {
  MarcadoAsistencia,
  MarcarEntradaRequest,
  MarcarSalidaRequest,
  EditarMarcadoRequest,
  EstadoHoyResponse,
  ObtenerMarcadosParams,
  DetectarAusenciasRequest,
  TipoTurno
} from './Asistencia';

// Deudas
export type {
  DeudaHoras,
  Justificacion,
  JustificarDeudaRequest,
  EstadoJustificacion,
  EstadoDeuda,
  MotivoDeuda
} from './Deuda';

// Configuración de Asistencia
export type {
  ConfiguracionAsistencia,
  ActualizarConfiguracionRequest,
  PoliticaHorasExtras,
  PeriodoLimite
} from './ConfiguracionAsistencia';
