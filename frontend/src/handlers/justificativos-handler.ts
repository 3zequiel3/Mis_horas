/**
 * Handler para gestión de justificativos
 * - Empleados pueden solicitar justificativos por ausencias/retrasos
 * - Admins pueden aprobar/rechazar justificativos
 */

import Swal from 'sweetalert2';
import { AlertUtils } from '../utils/swal';
import type { Dia, Empleado, Proyecto } from '../types';

interface Justificativo {
  id: number;
  dia_id: number;
  empleado_id: number;
  fecha: string;
  tipo: 'ausencia' | 'retraso' | 'salida_temprana' | 'otro';
  motivo: string;
  descripcion?: string;
  estado: 'pendiente' | 'aprobado' | 'rechazado';
  fecha_solicitud: string;
  fecha_resolucion?: string;
  resuelto_por?: number;
  observaciones_admin?: string;
}

export const JustificativosHandler = {
  /**
   * Mostrar modal de gestión de justificativos (ADMIN)
   */
  async mostrarGestion(proyecto: Proyecto): Promise<void> {
    try {
      // Cargar justificativos pendientes y recientes
      const justificativos = await this.cargarJustificativos(proyecto.id);
      
      const pendientes = justificativos.filter(j => j.estado === 'pendiente');
      const resueltos = justificativos.filter(j => j.estado !== 'pendiente').slice(0, 10);

      const { value: tab } = await Swal.fire({
        title: '📋 Gestión de Justificativos',
        html: `
          <div style="text-align: left;">
            <div class="justificativos-tabs" style="display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1);">
              <button class="justificativo-tab active" data-tab="pendientes" style="padding: 10px 20px; background: none; border: none; border-bottom: 2px solid #667eea; color: #667eea; cursor: pointer;">
                Pendientes (${pendientes.length})
              </button>
              <button class="justificativo-tab" data-tab="resueltos" style="padding: 10px 20px; background: none; border: none; color: #9ca3af; cursor: pointer;">
                Resueltos (${resueltos.length})
              </button>
            </div>

            <div id="tab-pendientes" class="justificativo-tab-content">
              ${pendientes.length === 0 ? `
                <div style="text-align: center; padding: 40px 20px; color: #9ca3af;">
                  <p>✅ No hay justificativos pendientes</p>
                </div>
              ` : this.renderizarListaJustificativos(pendientes, true)}
            </div>

            <div id="tab-resueltos" class="justificativo-tab-content" style="display: none;">
              ${resueltos.length === 0 ? `
                <div style="text-align: center; padding: 40px 20px; color: #9ca3af;">
                  <p>No hay justificativos resueltos</p>
                </div>
              ` : this.renderizarListaJustificativos(resueltos, false)}
            </div>
          </div>
        `,
        width: '700px',
        showCancelButton: true,
        confirmButtonText: 'Cerrar',
        showConfirmButton: true,
        cancelButtonText: '',
        background: '#0f1419',
        color: '#c8c8c8',
        confirmButtonColor: '#667eea',
        didOpen: () => {
          // Tabs
          const tabs = document.querySelectorAll('.justificativo-tab');
          tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
              const target = e.target as HTMLElement;
              const tabName = target.getAttribute('data-tab');
              
              tabs.forEach(t => {
                t.classList.remove('active');
                (t as HTMLElement).style.borderBottom = 'none';
                (t as HTMLElement).style.color = '#9ca3af';
              });
              
              target.classList.add('active');
              target.style.borderBottom = '2px solid #667eea';
              target.style.color = '#667eea';
              
              document.querySelectorAll('.justificativo-tab-content').forEach(content => {
                (content as HTMLElement).style.display = 'none';
              });
              
              const contentEl = document.getElementById(`tab-${tabName}`);
              if (contentEl) contentEl.style.display = 'block';
            });
          });

          // Botones de acción
          const aprobarBtns = document.querySelectorAll('.btn-aprobar-justificativo');
          aprobarBtns.forEach(btn => {
            btn.addEventListener('click', async (e) => {
              const id = parseInt((e.target as HTMLElement).getAttribute('data-id') || '0');
              await this.aprobarJustificativo(id);
              Swal.close();
              this.mostrarGestion(proyecto);
            });
          });

          const rechazarBtns = document.querySelectorAll('.btn-rechazar-justificativo');
          rechazarBtns.forEach(btn => {
            btn.addEventListener('click', async (e) => {
              const id = parseInt((e.target as HTMLElement).getAttribute('data-id') || '0');
              await this.rechazarJustificativo(id);
              Swal.close();
              this.mostrarGestion(proyecto);
            });
          });
        },
      });
    } catch (error) {
      console.error('Error mostrando justificativos:', error);
      AlertUtils.toast('Error al cargar justificativos', 'error');
    }
  },

  /**
   * Renderizar lista de justificativos
   */
  renderizarListaJustificativos(justificativos: Justificativo[], mostrarAcciones: boolean): string {
    const iconosTipo: Record<string, string> = {
      ausencia: '❌',
      retraso: '⏰',
      salida_temprana: '🚪',
      otro: '📝',
    };

    const colorEstado: Record<string, string> = {
      pendiente: '#f59e0b',
      aprobado: '#10b981',
      rechazado: '#ef4444',
    };

    return `
      <div style="max-height: 400px; overflow-y: auto;">
        ${justificativos.map(j => {
          const fecha = new Date(j.fecha);
          const fechaSolicitud = new Date(j.fecha_solicitud);

          return `
            <div style="background: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 3px solid ${colorEstado[j.estado]};">
              <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                <div>
                  <div style="color: #c8c8c8; font-weight: 600; margin-bottom: 5px;">
                    ${iconosTipo[j.tipo]} ${j.tipo.replace('_', ' ').toUpperCase()}
                  </div>
                  <div style="color: #9ca3af; font-size: 0.9em;">
                    📅 ${fecha.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })}
                  </div>
                </div>
                <span style="background: ${colorEstado[j.estado]}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">
                  ${j.estado}
                </span>
              </div>

              <div style="margin-bottom: 10px;">
                <strong style="color: #c8c8c8;">Motivo:</strong>
                <p style="color: #9ca3af; margin: 5px 0;">${j.motivo}</p>
              </div>

              ${j.descripcion ? `
                <div style="margin-bottom: 10px;">
                  <strong style="color: #c8c8c8;">Descripción:</strong>
                  <p style="color: #9ca3af; margin: 5px 0; font-size: 0.9em;">${j.descripcion}</p>
                </div>
              ` : ''}

              ${j.observaciones_admin ? `
                <div style="margin-bottom: 10px; padding: 10px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
                  <strong style="color: #c8c8c8;">Observaciones del administrador:</strong>
                  <p style="color: #9ca3af; margin: 5px 0; font-size: 0.9em;">${j.observaciones_admin}</p>
                </div>
              ` : ''}

              <div style="color: #6b7280; font-size: 0.8em; margin-top: 10px;">
                Solicitado ${fechaSolicitud.toLocaleDateString('es-ES')} a las ${fechaSolicitud.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
              </div>

              ${mostrarAcciones ? `
                <div style="display: flex; gap: 8px; margin-top: 12px;">
                  <button class="btn-aprobar-justificativo" data-id="${j.id}" style="flex: 1; padding: 8px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">
                    ✓ Aprobar
                  </button>
                  <button class="btn-rechazar-justificativo" data-id="${j.id}" style="flex: 1; padding: 8px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">
                    ✗ Rechazar
                  </button>
                </div>
              ` : ''}
            </div>
          `;
        }).join('')}
      </div>
    `;
  },

  /**
   * Solicitar justificativo (EMPLEADO)
   */
  async solicitarJustificativo(dia: Dia, empleado: Empleado, proyecto: Proyecto): Promise<void> {
    const { value: formValues } = await Swal.fire({
      title: '📝 Solicitar Justificativo',
      html: `
        <div style="text-align: left;">
          <p style="color: #9ca3af; margin-bottom: 20px;">
            Día: ${new Date(dia.fecha).toLocaleDateString('es-ES', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })}
          </p>

          <div style="margin-bottom: 15px;">
            <label style="display: block; color: #c8c8c8; margin-bottom: 8px; font-weight: 500;">
              Tipo de justificativo:
            </label>
            <select id="tipo-justificativo" class="swal2-input" style="width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: #c8c8c8;">
              <option value="ausencia">❌ Ausencia completa</option>
              <option value="retraso">⏰ Retraso</option>
              <option value="salida_temprana">🚪 Salida temprana</option>
              <option value="otro">📝 Otro</option>
            </select>
          </div>

          <div style="margin-bottom: 15px;">
            <label style="display: block; color: #c8c8c8; margin-bottom: 8px; font-weight: 500;">
              Motivo: *
            </label>
            <input type="text" id="motivo-justificativo" class="swal2-input" placeholder="Ej: Consulta médica" style="width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: #c8c8c8;">
          </div>

          <div style="margin-bottom: 15px;">
            <label style="display: block; color: #c8c8c8; margin-bottom: 8px; font-weight: 500;">
              Descripción adicional (opcional):
            </label>
            <textarea id="descripcion-justificativo" class="swal2-textarea" rows="3" placeholder="Información adicional que consideres relevante..." style="width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: #c8c8c8; resize: vertical;"></textarea>
          </div>
        </div>
      `,
      width: '550px',
      showCancelButton: true,
      confirmButtonText: 'Enviar Solicitud',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#667eea',
      cancelButtonColor: '#6b7280',
      preConfirm: () => {
        const tipo = (document.getElementById('tipo-justificativo') as HTMLSelectElement).value;
        const motivo = (document.getElementById('motivo-justificativo') as HTMLInputElement).value;
        const descripcion = (document.getElementById('descripcion-justificativo') as HTMLTextAreaElement).value;

        if (!motivo.trim()) {
          Swal.showValidationMessage('El motivo es obligatorio');
          return false;
        }

        return { tipo, motivo, descripcion };
      },
    });

    if (formValues) {
      try {
        // TODO: Implementar servicio para crear justificativo
        // await JustificativoService.crear({
        //   dia_id: dia.id,
        //   empleado_id: empleado.id,
        //   tipo: formValues.tipo,
        //   motivo: formValues.motivo,
        //   descripcion: formValues.descripcion,
        // });

        AlertUtils.toast('Justificativo enviado correctamente', 'success');
        
        // Notificar al administrador
        // await NotificacionService.crearNotificacion({
        //   usuario_id: proyecto.usuario_id,
        //   tipo: 'recordatorio',
        //   titulo: 'Nuevo justificativo pendiente',
        //   mensaje: `${empleado.nombre} solicitó un justificativo para el ${new Date(dia.fecha).toLocaleDateString()}`,
        // });
      } catch (error) {
        console.error('Error creando justificativo:', error);
        AlertUtils.toast('Error al enviar justificativo', 'error');
      }
    }
  },

  /**
   * Aprobar justificativo
   */
  async aprobarJustificativo(id: number): Promise<void> {
    const { value: observaciones } = await Swal.fire({
      title: '✓ Aprobar Justificativo',
      input: 'textarea',
      inputLabel: 'Observaciones (opcional):',
      inputPlaceholder: 'Comentarios adicionales...',
      showCancelButton: true,
      confirmButtonText: 'Aprobar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#10b981',
      cancelButtonColor: '#6b7280',
      inputAttributes: {
        style: 'background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #c8c8c8;'
      },
    });

    if (observaciones !== undefined) {
      try {
        // TODO: Implementar servicio
        // await JustificativoService.aprobar(id, observaciones);
        AlertUtils.toast('Justificativo aprobado', 'success');
      } catch (error) {
        console.error('Error aprobando justificativo:', error);
        AlertUtils.toast('Error al aprobar justificativo', 'error');
      }
    }
  },

  /**
   * Rechazar justificativo
   */
  async rechazarJustificativo(id: number): Promise<void> {
    const { value: observaciones } = await Swal.fire({
      title: '✗ Rechazar Justificativo',
      input: 'textarea',
      inputLabel: 'Motivo del rechazo: *',
      inputPlaceholder: 'Explica por qué se rechaza...',
      showCancelButton: true,
      confirmButtonText: 'Rechazar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#6b7280',
      inputValidator: (value) => {
        if (!value.trim()) {
          return 'Debes indicar el motivo del rechazo';
        }
        return null;
      },
      inputAttributes: {
        style: 'background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #c8c8c8;'
      },
    });

    if (observaciones) {
      try {
        // TODO: Implementar servicio
        // await JustificativoService.rechazar(id, observaciones);
        AlertUtils.toast('Justificativo rechazado', 'info');
      } catch (error) {
        console.error('Error rechazando justificativo:', error);
        AlertUtils.toast('Error al rechazar justificativo', 'error');
      }
    }
  },

  /**
   * Ver historial de justificativos del empleado
   */
  async verHistorialEmpleado(empleadoId: number, proyectoId: number): Promise<void> {
    try {
      const justificativos = await this.cargarJustificativos(proyectoId, empleadoId);

      const aprobados = justificativos.filter(j => j.estado === 'aprobado').length;
      const rechazados = justificativos.filter(j => j.estado === 'rechazado').length;
      const pendientes = justificativos.filter(j => j.estado === 'pendiente').length;

      await Swal.fire({
        title: '📊 Historial de Justificativos',
        html: `
          <div style="text-align: left;">
            <div style="display: flex; gap: 15px; margin-bottom: 20px;">
              <div style="flex: 1; background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5em; color: #10b981; font-weight: bold;">${aprobados}</div>
                <div style="color: #9ca3af; font-size: 0.9em;">Aprobados</div>
              </div>
              <div style="flex: 1; background: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5em; color: #ef4444; font-weight: bold;">${rechazados}</div>
                <div style="color: #9ca3af; font-size: 0.9em;">Rechazados</div>
              </div>
              <div style="flex: 1; background: rgba(245, 158, 11, 0.1); padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5em; color: #f59e0b; font-weight: bold;">${pendientes}</div>
                <div style="color: #9ca3af; font-size: 0.9em;">Pendientes</div>
              </div>
            </div>

            ${justificativos.length === 0 ? `
              <div style="text-align: center; padding: 40px 20px; color: #9ca3af;">
                <p>No hay justificativos registrados</p>
              </div>
            ` : this.renderizarListaJustificativos(justificativos, false)}
          </div>
        `,
        width: '700px',
        confirmButtonText: 'Cerrar',
        background: '#0f1419',
        color: '#c8c8c8',
        confirmButtonColor: '#667eea',
      });
    } catch (error) {
      console.error('Error cargando historial:', error);
      AlertUtils.toast('Error al cargar historial', 'error');
    }
  },

  /**
   * Cargar justificativos
   */
  async cargarJustificativos(proyectoId: number, empleadoId?: number): Promise<Justificativo[]> {
    try {
      // TODO: Implementar servicio real
      // const justificativos = await JustificativoService.getJustificativos(proyectoId, empleadoId);
      // return justificativos;

      // Mock data para desarrollo
      return [
        {
          id: 1,
          dia_id: 1,
          empleado_id: 1,
          fecha: '2025-11-18',
          tipo: 'ausencia',
          motivo: 'Consulta médica',
          descripcion: 'Tenía turno con el dentista a las 9:00',
          estado: 'pendiente',
          fecha_solicitud: '2025-11-18T10:30:00',
        },
        {
          id: 2,
          dia_id: 2,
          empleado_id: 1,
          fecha: '2025-11-15',
          tipo: 'retraso',
          motivo: 'Problema con el transporte',
          estado: 'aprobado',
          fecha_solicitud: '2025-11-15T09:30:00',
          fecha_resolucion: '2025-11-15T10:00:00',
          observaciones_admin: 'Aprobado. Recordar avisar con anticipación.',
        },
      ] as Justificativo[];
    } catch (error) {
      console.error('Error cargando justificativos:', error);
      return [];
    }
  },
};

// Exponer globalmente
(window as any).JustificativosHandler = JustificativosHandler;
