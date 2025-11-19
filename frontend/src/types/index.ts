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

// Comunes
export type {
  ErrorResponse,
  SuccessResponse,
  Estadisticas,
  TabConfig
} from './Common';
