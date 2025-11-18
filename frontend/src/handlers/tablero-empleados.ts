// Handler específico para tableros con empleados

import type { Proyecto, Empleado, Dia, Usuario } from '../types';
import { ProyectoService } from '../services/proyecto';
import { EmpleadosService } from '../services/empleados';
import { DiaService } from '../services/dia';
import { showErrorModal } from '../utils/modals';
import { horasAFormato } from '../utils/formatters';
import { MESES_ES } from '../utils/formatters';
import Swal from 'sweetalert2';

interface TableroEmpleadosState {
  proyectoActual: Proyecto | null;
  empleados: Empleado[];
  mesActual: number;
  anioActual: number;
  usuarioActual: Usuario | null;
}

export const tableroEmpleadosHandlers = {
  state: {
    proyectoActual: null,
    empleados: [],
    mesActual: new Date().getMonth() + 1,
    anioActual: new Date().getFullYear(),
    usuarioActual: null,
  } as TableroEmpleadosState,

  /**
   * Carga el usuario actual
   */
  async loadCurrentUser(): Promise<void> {
    try {
      const usuarioStr = sessionStorage.getItem('usuario');
      if (usuarioStr) {
        this.state.usuarioActual = JSON.parse(usuarioStr);
      }
    } catch (error) {
      console.error('Error cargando usuario:', error);
    }
  },

  /**
   * Carga el proyecto
   */
  async loadProyecto(): Promise<void> {
    try {
      await this.loadCurrentUser();

      const path = window.location.pathname;
      const proyectoId = parseInt(path.split('/').pop() || '0');

      if (!proyectoId) {
        window.location.href = '/proyectos';
        return;
      }

      this.state.proyectoActual = await ProyectoService.getProyecto(proyectoId);

      if (!this.state.proyectoActual) {
        window.location.href = '/proyectos';
        return;
      }

      // Verificar que sea un proyecto con empleados
      if (this.state.proyectoActual.tipo_proyecto !== 'empleados') {
        window.location.href = `/proyecto/${proyectoId}`;
        return;
      }

      // Actualizar UI
      this.updateProjectHeader();

      // Establecer mes y año
      this.state.mesActual = this.state.proyectoActual.mes;
      this.state.anioActual = this.state.proyectoActual.anio;

      // Cargar empleados
      await this.loadProyectoConEmpleados();
    } catch (error) {
      console.error('Error cargando proyecto:', error);
      showErrorModal('Error', 'No se pudo cargar el tablero');
    }
  },

  /**
   * Actualiza el header del proyecto
   */
  updateProjectHeader(): void {
    if (!this.state.proyectoActual) return;

    const nombreEl = document.getElementById('proyecto-nombre');
    const periodoEl = document.getElementById('proyecto-periodo');
    const statusEl = document.getElementById('proyecto-status');
    const cardNombreEl = document.getElementById('tablero-card-nombre');
    const cardDescripcionEl = document.getElementById('tablero-card-descripcion');

    if (nombreEl) nombreEl.textContent = this.state.proyectoActual.nombre;
    if (periodoEl) {
      const mes = MESES_ES[this.state.proyectoActual.mes as keyof typeof MESES_ES];
      periodoEl.textContent = `${mes} ${this.state.proyectoActual.anio}`;
    }
    if (statusEl) {
      statusEl.textContent = this.state.proyectoActual.activo ? '✓ Activo' : '✗ Inactivo';
      statusEl.className = this.state.proyectoActual.activo ? 'badge badge-active' : 'badge badge-inactive';
    }

    // Actualizar tarjeta lateral
    if (cardNombreEl) cardNombreEl.textContent = this.state.proyectoActual.nombre;
    if (cardDescripcionEl) {
      cardDescripcionEl.textContent = this.state.proyectoActual.descripcion || 'Sin descripción';
    }

    // Actualizar botón finalizar
    const finalizarBtn = document.getElementById('finalizar-btn');
    if (finalizarBtn) {
      finalizarBtn.textContent = this.state.proyectoActual.activo ? '✅ Finalizar' : '🔄 Reactivar';
    }
  },

  /**
   * Actualiza estadísticas del tablero
   */
  updateTableroStats(): void {
    const totalEmpleadosEl = document.getElementById('total-empleados');
    const totalHorasEl = document.getElementById('total-horas');

    if (totalEmpleadosEl) {
      totalEmpleadosEl.textContent = this.state.empleados.length.toString();
    }

    // Calcular total de horas (se actualizará después de cargar días)
    if (totalHorasEl) {
      totalHorasEl.textContent = '00:00';
    }
  },

  /**
   * Renderiza la lista de gestión de empleados
   */
  renderEmpleadosManagement(): void {
    const managementList = document.getElementById('empleados-management-list');
    if (!managementList) return;

    if (this.state.empleados.length === 0) {
      managementList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No hay empleados</p>';
      return;
    }

    managementList.innerHTML = this.state.empleados.map(emp => `
      <div class="empleado-management-item">
        <span class="empleado-management-name">${emp.nombre}</span>
        <div class="empleado-management-actions">
          <button class="btn-icon btn-editar-empleado" title="Editar" data-empleado-id="${emp.id}" data-empleado-nombre="${emp.nombre}">
            ✏️
          </button>
          <button class="btn-icon btn-danger btn-eliminar-empleado" title="Eliminar" data-empleado-id="${emp.id}" data-empleado-nombre="${emp.nombre}">
            🗑️
          </button>
        </div>
      </div>
    `).join('');

    // Event listeners para botones de editar
    document.querySelectorAll('.btn-editar-empleado').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.currentTarget as HTMLElement;
        const empleadoId = parseInt(target.dataset.empleadoId || '0');
        const empleadoNombre = target.dataset.empleadoNombre || '';
        if (empleadoId) {
          this.mostrarModalEditarEmpleado(empleadoId, empleadoNombre);
        }
      });
    });

    // Event listeners para botones de eliminar
    document.querySelectorAll('.btn-eliminar-empleado').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.currentTarget as HTMLElement;
        const empleadoId = parseInt(target.dataset.empleadoId || '0');
        const empleadoNombre = target.dataset.empleadoNombre || '';
        if (empleadoId) {
          this.eliminarEmpleado(empleadoId, empleadoNombre);
        }
      });
    });
  },

  /**
   * Obtiene la semana actual (7 días desde hoy)
   */
  getSemanActual(): string[] {
    const hoy = new Date();
    const semana: string[] = [];
    
    for (let i = 0; i < 7; i++) {
      const fecha = new Date(hoy);
      fecha.setDate(hoy.getDate() + i);
      semana.push(fecha.toISOString().split('T')[0]);
    }
    
    return semana;
  },

  /**
   * Carga proyecto con empleados - muestra tabla por cada empleado
   */
  async loadProyectoConEmpleados(): Promise<void> {
    try {
      if (!this.state.proyectoActual) return;

      const empleados = await EmpleadosService.getEmpleadosByProyecto(this.state.proyectoActual.id);
      this.state.empleados = empleados;

      const diasColumn = document.getElementById('empleados-container');
      if (!diasColumn) return;

      // Actualizar stats y management
      this.updateTableroStats();
      this.renderEmpleadosManagement();

      // Limpiar contenido
      diasColumn.innerHTML = '';

      if (empleados.length === 0) {
        diasColumn.innerHTML = `
          <div class="empty-state">
            <p>📭 No hay empleados en este tablero</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem;">Agrega empleados para comenzar</p>
            <button class="btn btn-primary" onclick="document.getElementById('add-empleado-btn').click()">
              ➕ Agregar Primer Empleado
            </button>
          </div>
        `;
        return;
      }

      // Crear sección por cada empleado
      for (let i = 0; i < empleados.length; i++) {
        const empleado = empleados[i];
        const isFirst = i === 0; // El primero estará abierto por defecto
        
        const diasEmpleado = await DiaService.getDiasMes(
          this.state.proyectoActual.id,
          this.state.anioActual,
          this.state.mesActual,
          empleado.id
        );

        // Obtener semana actual
        const semanaFechas = this.getSemanActual();
        const diasSemana = diasEmpleado.filter((dia) => {
          const diaFecha = new Date(dia.fecha).toISOString().split('T')[0];
          return semanaFechas.includes(diaFecha);
        });

        // Calcular totales
        const totalTrabajadas = diasSemana.reduce((sum, dia) => sum + (dia.horas_trabajadas || 0), 0);
        const totalReales = diasSemana.reduce((sum, dia) => sum + (dia.horas_reales || 0), 0);

        // Crear HTML para el empleado con acordeón
        const seccionHTML = `
          <div class="empleado-section" data-empleado-id="${empleado.id}">
            <div class="empleado-accordion-header ${isFirst ? 'active' : ''}" data-empleado-accordion="${empleado.id}">
              <div class="empleado-header-info">
                <h2>${empleado.nombre}</h2>
                <span class="empleado-hours-badge">${horasAFormato(totalTrabajadas)}</span>
              </div>
            </div>
            
            <div class="empleado-accordion-content ${isFirst ? 'active' : ''}" data-empleado-content="${empleado.id}">
              <div class="empleado-content-inner">
                <div class="table-container">
                  <table class="dias-table">
                    <thead>
                      <tr>
                        <th>Fecha</th>
                        <th>Día</th>
                        <th>Horas Trabajadas</th>
                        ${this.state.proyectoActual.horas_reales_activas ? '<th>Horas Reales</th>' : ''}
                      </tr>
                    </thead>
                    <tbody id="dias-tbody-${empleado.id}">
                      ${this.renderDiasEmpleado(diasSemana, this.state.proyectoActual.horas_reales_activas || false)}
                    </tbody>
                    <tfoot>
                      <tr class="totals-row">
                        <td><strong>Total:</strong></td>
                        <td></td>
                        <td><strong>${horasAFormato(totalTrabajadas)}</strong></td>
                        ${this.state.proyectoActual.horas_reales_activas ? `<td><strong>${horasAFormato(totalReales)}</strong></td>` : ''}
                      </tr>
                    </tfoot>
                  </table>
                </div>

                <div class="empleado-actions">
                  <button class="btn btn-primary-outline btn-ver-mes-empleado" data-empleado-id="${empleado.id}" data-empleado-nombre="${empleado.nombre}">
                    📅 Ver Todo el Mes
                  </button>
                  <button class="btn btn-danger btn-export-empleado" data-empleado-id="${empleado.id}" data-empleado-nombre="${empleado.nombre}">
                    📥 Exportar PDF
                  </button>
                </div>
              </div>
            </div>
          </div>
        `;

        diasColumn.insertAdjacentHTML('beforeend', seccionHTML);
      }

      // Agregar event listeners para acordeones
      document.querySelectorAll('.empleado-accordion-header').forEach(header => {
        header.addEventListener('click', (e) => {
          const target = e.currentTarget as HTMLElement;
          const empleadoId = target.dataset.empleadoAccordion;
          
          // Toggle del acordeón clickeado
          const content = document.querySelector(`[data-empleado-content="${empleadoId}"]`) as HTMLElement;
          const isActive = target.classList.contains('active');
          
          if (isActive) {
            target.classList.remove('active');
            content.classList.remove('active');
          } else {
            target.classList.add('active');
            content.classList.add('active');
          }
        });
      });

      // Agregar event listeners para exportar
      document.querySelectorAll('.btn-export-empleado').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const target = e.currentTarget as HTMLElement;
          const empleadoId = target.dataset.empleadoId;
          const empleadoNombre = target.dataset.empleadoNombre;
          if (empleadoId && empleadoNombre) {
            this.exportarPDFEmpleado(parseInt(empleadoId), empleadoNombre);
          }
        });
      });

      // Agregar event listeners para inputs de horas
      document.querySelectorAll('.horas-input').forEach(input => {
        input.addEventListener('blur', async (e) => {
          const target = e.target as HTMLInputElement;
          const diaId = parseInt(target.dataset.diaId || '0');
          const horas = target.value;

          if (diaId && horas) {
            try {
              await DiaService.updateHoras(diaId, horas);
              // Recargar para actualizar totales
              await this.loadProyectoConEmpleados();
            } catch (error) {
              console.error('Error actualizando horas:', error);
            }
          }
        });

        // También al presionar Enter
        input.addEventListener('keypress', (e: Event) => {
          const keyEvent = e as KeyboardEvent;
          if (keyEvent.key === 'Enter') {
            (e.target as HTMLInputElement).blur();
          }
        });
      });

    } catch (error) {
      console.error('Error cargando proyecto con empleados:', error);
    }
  },

  /**
   * Renderiza los días de un empleado
   */
  renderDiasEmpleado(dias: Dia[], mostrarHorasReales: boolean): string {
    if (!dias.length) {
      return `<tr><td colspan="${mostrarHorasReales ? 4 : 3}" class="text-center">No hay días para mostrar</td></tr>`;
    }

    return dias.map(dia => {
      const fecha = new Date(dia.fecha);
      const horasTrabajadas = horasAFormato(dia.horas_trabajadas || 0);
      const horasReales = horasAFormato(dia.horas_reales || 0);

      return `
        <tr data-dia-id="${dia.id}">
          <td>${fecha.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })}</td>
          <td>${dia.dia_semana}</td>
          <td>
            <input 
              type="text" 
              class="horas-input" 
              value="${horasTrabajadas}" 
              data-dia-id="${dia.id}"
              placeholder="00:00"
            />
          </td>
          ${mostrarHorasReales ? `<td>${horasReales}</td>` : ''}
        </tr>
      `;
    }).join('');
  },

  /**
   * Exporta PDF de un empleado específico
   */
  async exportarPDFEmpleado(empleadoId: number, empleadoNombre: string): Promise<void> {
    console.log('Exportando PDF para empleado:', empleadoId, empleadoNombre);
    // TODO: Implementar exportación de PDF
  },

  async mostrarModalConfiguracion(): Promise<void> {
    const { value: formValues } = await Swal.fire({
      title: 'Configuración del Proyecto',
      html: `
        <div style="text-align: left; padding: 10px;">
          <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
            <input 
              type="checkbox" 
              id="horas-reales-checkbox" 
              ${this.state.proyectoActual?.horas_reales_activas ? 'checked' : ''}
              style="width: 18px; height: 18px; cursor: pointer;"
            >
            <span style="font-size: 15px; color: #c8c8c8;">Activar columna de Horas Reales</span>
          </label>
          <p style="color: #9ca3af; font-size: 13px; margin-top: 10px; margin-left: 28px;">
            Cuando está activada, se mostrará una columna adicional para registrar las horas reales trabajadas.
          </p>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: 'Guardar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#667eea',
      cancelButtonColor: '#2d3746',
      preConfirm: () => {
        const checkbox = document.getElementById('horas-reales-checkbox') as HTMLInputElement;
        return {
          horas_reales_activas: checkbox.checked
        };
      }
    });

    if (formValues && this.state.proyectoActual) {
      try {
        await ProyectoService.updateConfiguracion(
          this.state.proyectoActual.id,
          { horas_reales_activas: formValues.horas_reales_activas }
        );
        
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

        // Recargar página completa para aplicar cambios
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
  },

  async mostrarModalEditarEmpleado(empleadoId: number, nombreActual: string): Promise<void> {
    const { value: nuevoNombre } = await Swal.fire({
      title: 'Editar Empleado',
      input: 'text',
      inputLabel: 'Nombre del empleado',
      inputValue: nombreActual,
      showCancelButton: true,
      confirmButtonText: 'Guardar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#667eea',
      cancelButtonColor: '#2d3746',
      inputValidator: (value) => {
        if (!value || value.trim() === '') {
          return 'El nombre es requerido';
        }
        return null;
      }
    });

    if (nuevoNombre && nuevoNombre.trim() !== nombreActual) {
      try {
        await EmpleadosService.updateEmpleado(empleadoId, { nombre: nuevoNombre.trim() });
        
        Swal.fire({
          icon: 'success',
          title: 'Empleado actualizado',
          showConfirmButton: false,
          timer: 1500,
          background: '#0f1419',
          color: '#c8c8c8',
          iconColor: '#10b981'
        });

        // Recargar para mostrar cambios
        await this.loadProyectoConEmpleados();
      } catch (error) {
        console.error('Error actualizando empleado:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo actualizar el empleado',
          background: '#0f1419',
          color: '#c8c8c8',
          iconColor: '#ef4444',
          confirmButtonColor: '#ef4444'
        });
      }
    }
  },

  async eliminarEmpleado(empleadoId: number, nombreEmpleado: string): Promise<void> {
    const result = await Swal.fire({
      title: '¿Eliminar empleado?',
      html: `
        <p style="color: #c8c8c8;">¿Estás seguro de que deseas eliminar a <strong>${nombreEmpleado}</strong>?</p>
        <p style="color: #ef4444; font-size: 14px; margin-top: 10px;">
          ⚠️ Se eliminarán todos los registros de horas asociados a este empleado.
        </p>
      `,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#2d3746',
      iconColor: '#f59e0b'
    });

    if (result.isConfirmed) {
      try {
        await EmpleadosService.deleteEmpleado(empleadoId);
        
        Swal.fire({
          icon: 'success',
          title: 'Empleado eliminado',
          showConfirmButton: false,
          timer: 1500,
          background: '#0f1419',
          color: '#c8c8c8',
          iconColor: '#10b981'
        });

        // Recargar para mostrar cambios
        await this.loadProyectoConEmpleados();
      } catch (error) {
        console.error('Error eliminando empleado:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo eliminar el empleado',
          background: '#0f1419',
          color: '#c8c8c8',
          iconColor: '#ef4444',
          confirmButtonColor: '#ef4444'
        });
      }
    }
  },

  /**
   * Carga las tareas del proyecto y las muestra en el panel lateral
   */
  async loadTareas(): Promise<void> {
    try {
      if (!this.state.proyectoActual) return;

      const { TareaService } = await import('../services/tarea');
      const tareas = await TareaService.getTareasProyecto(this.state.proyectoActual.id);
      
      const tareasList = document.getElementById('tareas-list');
      const tareasCount = document.getElementById('tareas-count');
      
      if (!tareasList) return;

      if (tareasCount) {
        tareasCount.textContent = tareas.length.toString();
      }

      if (tareas.length === 0) {
        tareasList.innerHTML = `
          <div class="empty-tareas">
            <p>📭 Sin tareas aún</p>
          </div>
        `;
        return;
      }

      tareasList.innerHTML = tareas.map((tarea: any) => `
        <div class="tarea-item" data-tarea-id="${tarea.id}">
          <div class="tarea-header">
            <h4 class="tarea-titulo">${tarea.titulo}</h4>
            <span class="tarea-horas">${tarea.horas || '00:00'}</span>
          </div>
          ${tarea.detalle ? `<p class="tarea-detalle">${tarea.detalle}</p>` : ''}
          <div class="tarea-footer">
            <span class="tarea-dias-count">${tarea.dias?.length || 0} días</span>
          </div>
        </div>
      `).join('');

      // Agregar eventos de click a las tareas
      const tareaItems = tareasList.querySelectorAll('.tarea-item');
      tareaItems.forEach(item => {
        item.addEventListener('click', async () => {
          const tareaId = parseInt(item.getAttribute('data-tarea-id') || '0');
          const tarea = tareas.find((t: any) => t.id === tareaId);
          if (tarea) {
            const { TareaHandler } = await import('./tarea');
            const viewModal = document.getElementById('view-tarea-modal');
            const viewBody = document.getElementById('view-modal-body');
            
            if (viewModal && viewBody) {
              const mostrarHorasReales = this.state.proyectoActual?.horas_reales_activas || false;
              TareaHandler.renderizarVistaDetalle(tarea, mostrarHorasReales);
              viewModal.style.display = 'flex';

              // Configurar botones de editar y eliminar
              const editBtn = document.getElementById('edit-from-view-btn');
              const deleteBtn = document.getElementById('delete-from-view-btn');

              if (editBtn) {
                editBtn.onclick = async () => {
                  viewModal.style.display = 'none';
                  await TareaHandler.cargarParaEditar(
                    tarea,
                    this.state.proyectoActual!.id,
                    this.state.anioActual,
                    this.state.mesActual
                  );
                  const modal = document.getElementById('tarea-modal');
                  if (modal) modal.style.display = 'flex';
                };
              }

              if (deleteBtn) {
                deleteBtn.onclick = async () => {
                  viewModal.style.display = 'none';
                  await TareaHandler.eliminarTarea(tarea.id, tarea.titulo, async () => {
                    await this.loadTareas();
                  });
                };
              }
            }
          }
        });
      });
    } catch (error) {
      console.error('Error cargando tareas:', error);
    }
  },

  /**
   * Muestra modal con el mes completo de un empleado
   */
  async verMesCompletoEmpleado(empleadoId: number, nombreEmpleado: string): Promise<void> {
    try {
      if (!this.state.proyectoActual) return;

      const modal = document.getElementById('empleado-mes-modal');
      const modalTitle = document.getElementById('empleado-mes-modal-title');
      const tbody = document.getElementById('empleado-mes-dias-tbody');
      const totalTrabajadas = document.getElementById('empleado-mes-total-trabajadas');
      const totalReales = document.getElementById('empleado-mes-total-reales');
      const thHorasReales = document.getElementById('empleado-th-horas-reales');
      const tdTotalReales = document.getElementById('empleado-td-total-reales');

      if (!modal || !tbody) return;

      // Actualizar título
      if (modalTitle) {
        const mesNombre = MESES_ES[this.state.mesActual as keyof typeof MESES_ES];
        modalTitle.textContent = `${mesNombre} ${this.state.anioActual} - ${nombreEmpleado}`;
      }

      // Mostrar/ocultar columna de horas reales
      const mostrarHorasReales = this.state.proyectoActual.horas_reales_activas || false;
      if (thHorasReales) {
        thHorasReales.style.display = mostrarHorasReales ? '' : 'none';
      }
      if (tdTotalReales) {
        tdTotalReales.style.display = mostrarHorasReales ? '' : 'none';
      }

      // Cargar días del mes completo
      const dias = await DiaService.getDiasMes(
        this.state.proyectoActual.id,
        this.state.anioActual,
        this.state.mesActual,
        empleadoId
      );

      // Calcular totales
      const sumaHorasTrabajadas = dias.reduce((sum, dia) => sum + (dia.horas_trabajadas || 0), 0);
      const sumaHorasReales = dias.reduce((sum, dia) => sum + (dia.horas_reales || 0), 0);

      // Renderizar días
      tbody.innerHTML = this.renderDiasEmpleado(dias, mostrarHorasReales);

      // Actualizar totales
      if (totalTrabajadas) {
        totalTrabajadas.textContent = horasAFormato(sumaHorasTrabajadas);
      }
      if (totalReales) {
        totalReales.textContent = horasAFormato(sumaHorasReales);
      }

      // Mostrar modal
      modal.style.display = 'flex';

      // Cerrar modal
      const closeBtn = document.getElementById('empleado-mes-modal-close');
      const closeBtnFooter = document.getElementById('empleado-mes-modal-close-btn');

      const closeHandler = () => {
        modal.style.display = 'none';
      };

      if (closeBtn) {
        closeBtn.onclick = closeHandler;
      }
      if (closeBtnFooter) {
        closeBtnFooter.onclick = closeHandler;
      }

      modal.onclick = (e) => {
        if (e.target === modal) {
          modal.style.display = 'none';
        }
      };
    } catch (error) {
      console.error('Error mostrando mes completo:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo cargar el mes completo',
        background: '#0f1419',
        color: '#c8c8c8',
        iconColor: '#ef4444',
        confirmButtonColor: '#ef4444'
      });
    }
  },
};
