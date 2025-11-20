/**
 * Handler para gestión de asistencia
 */

import { AsistenciaService } from '../services/asistencia';
import type { MarcarEntradaRequest, MarcarSalidaRequest } from '../types';

export const AsistenciaHandler = {
  /**
   * Marca la entrada de asistencia
   */
  async marcarEntrada(data: MarcarEntradaRequest): Promise<void> {
    try {
      const marcado = await AsistenciaService.marcarEntrada(data);
      
      // Mostrar mensaje de éxito
      alert(`✅ Entrada marcada exitosamente a las ${marcado.hora_entrada}`);
      
      // Recargar la página para actualizar el estado
      window.location.reload();
    } catch (error) {
      console.error('Error al marcar entrada:', error);
      alert(`❌ Error al marcar entrada: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },

  /**
   * Marca la salida de asistencia
   */
  async marcarSalida(data: MarcarSalidaRequest): Promise<void> {
    try {
      const marcado = await AsistenciaService.marcarSalida(data);
      
      // Mostrar mensaje de éxito
      alert(`✅ Salida marcada exitosamente a las ${marcado.hora_salida}`);
      
      // Recargar la página para actualizar el estado
      window.location.reload();
    } catch (error) {
      console.error('Error al marcar salida:', error);
      alert(`❌ Error al marcar salida: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },

  /**
   * Obtiene el estado de asistencia del día
   */
  async obtenerEstadoHoy(proyectoId: number, empleadoId: number): Promise<any> {
    try {
      return await AsistenciaService.obtenerEstadoHoy({
        proyecto_id: proyectoId,
        empleado_id: empleadoId,
      });
    } catch (error) {
      console.error('Error al obtener estado de asistencia:', error);
      return null;
    }
  },

  /**
   * Obtiene los marcados de asistencia
   */
  async obtenerMarcados(params: {
    proyecto_id?: number;
    empleado_id?: number;
    fecha_desde?: string;
    fecha_hasta?: string;
  }): Promise<any[]> {
    try {
      return await AsistenciaService.obtenerMarcados(params);
    } catch (error) {
      console.error('Error al obtener marcados:', error);
      return [];
    }
  },

  /**
   * Edita un marcado de asistencia (solo admin)
   */
  async editarMarcado(marcadoId: number, data: any): Promise<void> {
    try {
      await AsistenciaService.editarMarcado(marcadoId, data);
      alert('✅ Marcado editado exitosamente');
      window.location.reload();
    } catch (error) {
      console.error('Error al editar marcado:', error);
      alert(`❌ Error al editar marcado: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },

  /**
   * Confirma horas extras de un marcado (solo admin)
   */
  async confirmarHorasExtras(marcadoId: number, aprobar: boolean, observaciones?: string): Promise<void> {
    try {
      await AsistenciaService.confirmarHorasExtras(marcadoId, {
        aprobar,
        observaciones,
      });
      
      const mensaje = aprobar ? '✅ Horas extras aprobadas' : '❌ Horas extras rechazadas';
      alert(mensaje);
      window.location.reload();
    } catch (error) {
      console.error('Error al confirmar horas extras:', error);
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },
};
