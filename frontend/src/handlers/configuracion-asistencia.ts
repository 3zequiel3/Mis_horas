/**
 * Handler para configuración de asistencia
 */

import { ConfiguracionAsistenciaService } from '../services/configuracion-asistencia';
import type { ActualizarConfiguracionRequest } from '../types';

export const ConfiguracionAsistenciaHandler = {
  /**
   * Obtiene la configuración de asistencia de un proyecto
   */
  async obtenerConfiguracion(proyectoId: number): Promise<any> {
    try {
      return await ConfiguracionAsistenciaService.obtenerConfiguracion(proyectoId);
    } catch (error) {
      console.error('Error al obtener configuración:', error);
      return null;
    }
  },

  /**
   * Actualiza la configuración de asistencia
   */
  async actualizarConfiguracion(
    proyectoId: number,
    data: ActualizarConfiguracionRequest
  ): Promise<void> {
    try {
      await ConfiguracionAsistenciaService.actualizarConfiguracion(proyectoId, data);
      alert('✅ Configuración actualizada correctamente');
      window.location.reload();
    } catch (error) {
      console.error('Error al actualizar configuración:', error);
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },

  /**
   * Activa el modo de asistencia para un proyecto
   */
  async activarAsistencia(
    proyectoId: number,
    configuracionInicial?: ActualizarConfiguracionRequest
  ): Promise<void> {
    try {
      await ConfiguracionAsistenciaService.activarAsistencia(
        proyectoId,
        configuracionInicial
      );
      alert('✅ Sistema de asistencia activado correctamente');
      window.location.reload();
    } catch (error) {
      console.error('Error al activar asistencia:', error);
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },

  /**
   * Desactiva el modo de asistencia para un proyecto
   */
  async desactivarAsistencia(proyectoId: number): Promise<void> {
    const confirmar = confirm(
      '⚠️ ¿Está seguro de desactivar el sistema de asistencia?\n\n' +
      'Los marcados existentes se mantendrán pero no se podrán crear nuevos.'
    );

    if (!confirmar) return;

    try {
      await ConfiguracionAsistenciaService.desactivarAsistencia(proyectoId);
      alert('⚠️ Sistema de asistencia desactivado');
      window.location.reload();
    } catch (error) {
      console.error('Error al desactivar asistencia:', error);
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  },

  /**
   * Renderiza el formulario de configuración
   */
  renderFormulario(config: any, onSubmit: (data: ActualizarConfiguracionRequest) => void): string {
    return `
      <form id="config-asistencia-form" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Política de Horas Extras -->
          <div>
            <label class="block text-sm font-medium mb-1">
              Política de Horas Extras
            </label>
            <select name="politica_horas_extras" class="w-full border rounded px-3 py-2">
              <option value="compensar_deuda" ${config?.politica_horas_extras === 'compensar_deuda' ? 'selected' : ''}>
                Compensar Deuda
              </option>
              <option value="bloquear_extras" ${config?.politica_horas_extras === 'bloquear_extras' ? 'selected' : ''}>
                Bloquear Extras
              </option>
              <option value="separar_cuentas" ${config?.politica_horas_extras === 'separar_cuentas' ? 'selected' : ''}>
                Cuentas Separadas
              </option>
            </select>
          </div>

          <!-- Tolerancia de Retraso -->
          <div>
            <label class="block text-sm font-medium mb-1">
              Tolerancia de Retraso (minutos)
            </label>
            <input 
              type="number" 
              name="tolerancia_retraso_minutos"
              value="${config?.tolerancia_retraso_minutos || 15}"
              min="0"
              max="60"
              class="w-full border rounded px-3 py-2"
            />
          </div>

          <!-- Marcado Automático de Salida -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              name="marcar_salida_automatica"
              id="marcar_salida_automatica"
              ${config?.marcar_salida_automatica ? 'checked' : ''}
              class="mr-2"
            />
            <label for="marcar_salida_automatica" class="text-sm font-medium">
              Marcar Salida Automáticamente
            </label>
          </div>

          <!-- Permitir Justificaciones -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              name="permitir_justificaciones"
              id="permitir_justificaciones"
              ${config?.permitir_justificaciones ? 'checked' : ''}
              class="mr-2"
            />
            <label for="permitir_justificaciones" class="text-sm font-medium">
              Permitir Justificaciones
            </label>
          </div>

          <!-- Requiere Aprobación -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              name="requiere_aprobacion_justificaciones"
              id="requiere_aprobacion_justificaciones"
              ${config?.requiere_aprobacion_justificaciones ? 'checked' : ''}
              class="mr-2"
            />
            <label for="requiere_aprobacion_justificaciones" class="text-sm font-medium">
              Requiere Aprobación de Admin
            </label>
          </div>

          <!-- Enviar Recordatorios -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              name="enviar_recordatorio_marcado"
              id="enviar_recordatorio_marcado"
              ${config?.enviar_recordatorio_marcado ? 'checked' : ''}
              class="mr-2"
            />
            <label for="enviar_recordatorio_marcado" class="text-sm font-medium">
              Enviar Recordatorios de Marcado
            </label>
          </div>
        </div>

        <div class="flex justify-end space-x-2 mt-4">
          <button 
            type="button"
            onclick="window.history.back()"
            class="px-4 py-2 border rounded hover:bg-gray-100"
          >
            Cancelar
          </button>
          <button 
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Guardar Configuración
          </button>
        </div>
      </form>
    `;
  },
};
