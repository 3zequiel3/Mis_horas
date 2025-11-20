/**
 * Handler para configuración de horarios y turnos del tablero
 */

import Swal from 'sweetalert2';
import { ProyectosService } from '../services/proyectos';
import type { Proyecto } from '../types';

export const ConfigHorariosHandler = {
  /**
   * Mostrar modal de configuración de horarios
   */
  async mostrar(proyecto: Proyecto): Promise<void> {
    const { value: formValues } = await Swal.fire({
      title: 'Configuración de Horarios',
      width: '800px',
      html: `
        <div style="text-align: left; padding: 10px;">
          <!-- Horas Reales -->
          <div style="margin-bottom: 20px;">
            <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
              <input 
                type="checkbox" 
                id="horas-reales-checkbox" 
                ${proyecto.horas_reales_activas ? 'checked' : ''}
                style="width: 18px; height: 18px; cursor: pointer;"
              >
              <span style="font-size: 15px; color: #c8c8c8;">✅ Activar columna de Horas Reales</span>
            </label>
            <p style="color: #9ca3af; font-size: 13px; margin-top: 5px; margin-left: 28px;">
              Muestra una columna adicional para registrar las horas reales trabajadas.
            </p>
          </div>

          <!-- Sistema de Horarios -->
          <div style="margin-bottom: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
            <label style="display: block; margin-bottom: 10px; color: #c8c8c8; font-size: 15px; font-weight: 600;">
              ⏰ Sistema de Horarios
            </label>
            <select id="modo-horarios-select" style="width: 100%; padding: 10px; background: #1a1f2e; color: #c8c8c8; border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; margin-bottom: 15px; font-size: 14px;">
              <option value="corrido" ${proyecto.modo_horarios === 'corrido' ? 'selected' : ''}>De corrido (Entrada/Salida única)</option>
              <option value="turnos" ${proyecto.modo_horarios === 'turnos' ? 'selected' : ''}>Por turnos (Mañana/Tarde)</option>
            </select>

            <!-- Configuración de Turnos -->
            <div id="config-turnos" style="display: ${proyecto.modo_horarios === 'turnos' ? 'block' : 'none'};">
              <p style="color: #9ca3af; font-size: 13px; margin-bottom: 15px;">
                Define los rangos horarios permitidos para cada turno. Las horas extras se calcularán automáticamente.
              </p>
              
              <div style="margin-bottom: 15px; padding: 15px; background: rgba(102, 126, 234, 0.08); border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 8px;">
                <label style="display: block; margin-bottom: 10px; color: #c8c8c8; font-size: 14px; font-weight: 600;">🌅 Turno Mañana</label>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                  <div>
                    <label style="display: block; font-size: 12px; color: #9ca3af; margin-bottom: 4px;">Hora Inicio</label>
                    <input type="time" id="turno-manana-inicio" value="${proyecto.turno_manana_inicio || ''}" style="width: 100%; padding: 8px; background: #1a1f2e; color: #c8c8c8; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; font-size: 14px;">
                  </div>
                  <div>
                    <label style="display: block; font-size: 12px; color: #9ca3af; margin-bottom: 4px;">Hora Fin</label>
                    <input type="time" id="turno-manana-fin" value="${proyecto.turno_manana_fin || ''}" style="width: 100%; padding: 8px; background: #1a1f2e; color: #c8c8c8; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; font-size: 14px;">
                  </div>
                </div>
              </div>

              <div style="padding: 15px; background: rgba(118, 75, 162, 0.08); border: 1px solid rgba(118, 75, 162, 0.2); border-radius: 8px;">
                <label style="display: block; margin-bottom: 10px; color: #c8c8c8; font-size: 14px; font-weight: 600;">🌆 Turno Tarde</label>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                  <div>
                    <label style="display: block; font-size: 12px; color: #9ca3af; margin-bottom: 4px;">Hora Inicio</label>
                    <input type="time" id="turno-tarde-inicio" value="${proyecto.turno_tarde_inicio || ''}" style="width: 100%; padding: 8px; background: #1a1f2e; color: #c8c8c8; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; font-size: 14px;">
                  </div>
                  <div>
                    <label style="display: block; font-size: 12px; color: #9ca3af; margin-bottom: 4px;">Hora Fin</label>
                    <input type="time" id="turno-tarde-fin" value="${proyecto.turno_tarde_fin || ''}" style="width: 100%; padding: 8px; background: #1a1f2e; color: #c8c8c8; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; font-size: 14px;">
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: 'Guardar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#667eea',
      cancelButtonColor: '#2d3746',
      didOpen: () => {
        const modoSelect = document.getElementById('modo-horarios-select') as HTMLSelectElement;
        const configTurnos = document.getElementById('config-turnos') as HTMLElement;
        
        modoSelect?.addEventListener('change', () => {
          if (modoSelect.value === 'turnos') {
            configTurnos.style.display = 'block';
          } else {
            configTurnos.style.display = 'none';
          }
        });
      },
      preConfirm: () => {
        const horasReales = (document.getElementById('horas-reales-checkbox') as HTMLInputElement).checked;
        const modoHorarios = (document.getElementById('modo-horarios-select') as HTMLSelectElement).value;
        const turnoMananaInicio = (document.getElementById('turno-manana-inicio') as HTMLInputElement)?.value;
        const turnoMananaFin = (document.getElementById('turno-manana-fin') as HTMLInputElement)?.value;
        const turnoTardeInicio = (document.getElementById('turno-tarde-inicio') as HTMLInputElement)?.value;
        const turnoTardeFin = (document.getElementById('turno-tarde-fin') as HTMLInputElement)?.value;

        let horarioInicio = null;
        let horarioFin = null;
        
        if (modoHorarios === 'turnos' && turnoMananaInicio && turnoTardeFin) {
          horarioInicio = turnoMananaInicio;
          horarioFin = turnoTardeFin;
        }

        return {
          horas_reales_activas: horasReales,
          modo_horarios: modoHorarios,
          horario_inicio: horarioInicio,
          horario_fin: horarioFin,
          turno_manana_inicio: turnoMananaInicio || null,
          turno_manana_fin: turnoMananaFin || null,
          turno_tarde_inicio: turnoTardeInicio || null,
          turno_tarde_fin: turnoTardeFin || null,
        };
      }
    });

    if (formValues) {
      try {
        await ProyectosService.updateConfiguracion(proyecto.id, formValues);

        await Swal.fire({
          icon: 'success',
          title: 'Configuración actualizada',
          text: 'La página se recargará para aplicar los cambios',
          showConfirmButton: false,
          timer: 1500,
          background: '#0f1419',
          color: '#c8c8c8',
          iconColor: '#10b981'
        });

        window.location.reload();
      } catch (error) {
        console.error('Error actualizando configuración:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo actualizar la configuración',
          background: '#0f1419',
          color: '#c8c8c8',
          iconColor: '#ef4444',
          confirmButtonColor: '#ef4444'
        });
      }
    }
  }
};
