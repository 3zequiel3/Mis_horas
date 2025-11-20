/**
 * Handler para gestión de deudas y justificaciones
 */

import { DeudasService } from '../services/deudas';
import type { JustificarDeudaRequest } from '../types';

export const DeudasHandler = {
  /**
   * Obtiene la deuda de horas del empleado
   */
  async obtenerDeudaEmpleado(proyectoId: number, empleadoId: number): Promise<any> {
    try {
      return await DeudasService.obtenerDeudaEmpleado({
        proyecto_id: proyectoId,
        empleado_id: empleadoId,
      });
    } catch (error) {
      console.error('Error al obtener deuda:', error);
      return null;
    }
  },

  /**
   * Justifica una deuda de horas
   */
  async justificarDeuda(deudaId: number, data: JustificarDeudaRequest): Promise<void> {
    try {
      await DeudasService.justificarDeuda(deudaId, data);
      alert('✅ Justificación enviada correctamente. Pendiente de aprobación.');
      window.location.reload();
    } catch (error) {
      console.error('Error al justificar deuda:', error);
      alert(`❌ Error al enviar justificación: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },

  /**
   * Obtiene las justificaciones del empleado
   */
  async obtenerJustificacionesEmpleado(
    proyectoId: number, 
    empleadoId: number,
    estado?: 'pendiente' | 'aprobada' | 'rechazada'
  ): Promise<any[]> {
    try {
      return await DeudasService.obtenerJustificacionesEmpleado({
        proyecto_id: proyectoId,
        empleado_id: empleadoId,
        estado,
      });
    } catch (error) {
      console.error('Error al obtener justificaciones:', error);
      return [];
    }
  },

  /**
   * Obtiene todas las justificaciones de un proyecto (solo admin)
   */
  async obtenerJustificacionesProyecto(
    proyectoId: number,
    filtros?: { estado?: 'pendiente' | 'aprobada' | 'rechazada'; empleado_id?: number }
  ): Promise<any[]> {
    try {
      return await DeudasService.obtenerJustificacionesProyecto(proyectoId, filtros);
    } catch (error) {
      console.error('Error al obtener justificaciones del proyecto:', error);
      return [];
    }
  },

  /**
   * Aprueba una justificación (solo admin)
   */
  async aprobarJustificacion(justificacionId: number, observaciones?: string): Promise<void> {
    try {
      await DeudasService.aprobarJustificacion(justificacionId, {
        observaciones_admin: observaciones,
      });
      alert('✅ Justificación aprobada correctamente');
      window.location.reload();
    } catch (error) {
      console.error('Error al aprobar justificación:', error);
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },

  /**
   * Rechaza una justificación (solo admin)
   */
  async rechazarJustificacion(justificacionId: number, observaciones: string): Promise<void> {
    if (!observaciones || observaciones.trim() === '') {
      alert('⚠️ Debe proporcionar un motivo de rechazo');
      return;
    }

    try {
      await DeudasService.rechazarJustificacion(justificacionId, {
        observaciones_admin: observaciones,
      });
      alert('❌ Justificación rechazada');
      window.location.reload();
    } catch (error) {
      console.error('Error al rechazar justificación:', error);
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },
};
