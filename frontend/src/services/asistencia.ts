import { ApiService } from './api';
import type { 
  MarcadoAsistencia, 
  MarcarEntradaRequest, 
  MarcarSalidaRequest, 
  EditarMarcadoRequest, 
  EstadoHoyResponse 
} from '../types';

/**
 * Servicio para gestionar asistencia
 */
export class AsistenciaService extends ApiService {
  /**
   * Marca la entrada de asistencia
   * Backend espera: empleado_id, proyecto_id, fecha (opcional), hora (opcional)
   */
  static async marcarEntrada(data: MarcarEntradaRequest): Promise<MarcadoAsistencia> {
    // Backend espera "hora" no "hora_entrada"
    const payload = {
      empleado_id: data.empleado_id,
      proyecto_id: data.proyecto_id,
      fecha: data.fecha,
      hora: data.hora_entrada,
      latitud: data.latitud,
      longitud: data.longitud
    };
    return this.post('/api/asistencia/marcar-entrada', payload);
  }

  /**
   * Marca la salida de asistencia
   * Backend espera: empleado_id, proyecto_id, fecha (opcional), hora (opcional), confirmar_continuidad
   */
  static async marcarSalida(data: MarcarSalidaRequest): Promise<MarcadoAsistencia> {
    // Backend espera "hora" no "hora_salida" y no usa marcado_id
    const payload = {
      empleado_id: data.empleado_id,
      proyecto_id: data.proyecto_id,
      fecha: data.fecha,
      hora: data.hora_salida,
      confirmar_continuidad: data.confirmacion_continua,
      latitud: data.latitud,
      longitud: data.longitud
    };
    return this.post('/api/asistencia/marcar-salida', payload);
  }

  /**
   * Obtiene los marcados de asistencia
   */
  static async obtenerMarcados(params: {
    proyecto_id?: number;
    empleado_id?: number;
    fecha_desde?: string;
    fecha_hasta?: string;
    turno?: string;
    solo_pendientes?: boolean;
  }): Promise<MarcadoAsistencia[]> {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString());
      }
    });

    return this.get(`/api/asistencia/marcados?${queryParams.toString()}`);
  }

  /**
   * Detecta ausencias en un período
   */
  static async detectarAusencias(data: {
    proyecto_id: number;
    fecha_desde: string;
    fecha_hasta: string;
  }): Promise<{ ausencias: any[] }> {
    return this.post('/api/asistencia/detectar-ausencias', data);
  }

  /**
   * Obtiene el estado de asistencia del día actual
   */
  static async obtenerEstadoHoy(params: {
    proyecto_id: number;
    empleado_id: number;
  }): Promise<EstadoHoyResponse> {
    const queryParams = new URLSearchParams({
      proyecto_id: params.proyecto_id.toString(),
      empleado_id: params.empleado_id.toString(),
    });

    return this.get(`/api/asistencia/estado-hoy?${queryParams.toString()}`);
  }

  /**
   * Edita un marcado de asistencia (solo admin)
   */
  static async editarMarcado(
    marcadoId: number,
    data: EditarMarcadoRequest
  ): Promise<MarcadoAsistencia> {
    return this.put(`/api/asistencia/marcados/${marcadoId}/editar`, data);
  }

  /**
   * Confirma horas extras de un marcado (solo admin)
   */
  static async confirmarHorasExtras(
    marcadoId: number,
    data: { aprobar: boolean; observaciones?: string }
  ): Promise<MarcadoAsistencia> {
    // Backend espera la propiedad `confirmada`
    const payload = {
      confirmada: data.aprobar,
      observaciones: data.observaciones
    };
    return this.put(`/api/asistencia/marcados/${marcadoId}/confirmar-horas-extras`, payload);
  }
}
