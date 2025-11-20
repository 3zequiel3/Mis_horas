// Handler específico para tableros con empleados

import type { Proyecto, Empleado, Dia, Usuario } from '../types';
import { ProyectoService } from '../services/proyecto';
import { EmpleadosService } from '../services/empleados';
import { DiaService } from '../services/dia';
import { showErrorModal } from '../utils/modals';
import { horasAFormato, MESES_ES } from '../utils/formatters';
import { formatearFechaSinAnio } from '../utils/date';
import Swal from 'sweetalert2';

interface TableroEmpleadosState {
  proyectoActual: Proyecto | null;
  empleados: Empleado[];
  mesActual: number;
  anioActual: number;
  usuarioActual: Usuario | null;
}

export const TableroEmpleadosHandler = {
  state: {
    proyectoActual: null as Proyecto | null,
    empleados: [] as Empleado[],
    mesActual: 1,
    anioActual: new Date().getFullYear(),
    semanaInicio: new Date(),
    usuarioActual: null as Usuario | null,
  },

  // Mantener referencias de los handlers
  acordeonHandler: null as ((e: Event) => void) | null,
  blurHandler: null as ((e: Event) => void) | null,
  keypressHandler: null as ((e: Event) => void) | null,

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
  async updateTableroStats(): Promise<void> {
    const totalEmpleadosEl = document.getElementById('total-empleados');
    const totalHorasEl = document.getElementById('total-horas');

    if (totalEmpleadosEl) {
      totalEmpleadosEl.textContent = this.state.empleados.length.toString();
    }

    // Calcular total de horas sumando de todos los empleados
    if (totalHorasEl && this.state.proyectoActual) {
      let totalHoras = 0;

      for (const empleado of this.state.empleados) {
        const dias = await DiaService.getDiasMes(
          this.state.proyectoActual.id,
          this.state.anioActual,
          this.state.mesActual,
          empleado.id
        );
        totalHoras += dias.reduce((sum: number, dia: any) => sum + (dia.horas_trabajadas || 0), 0);
      }

      totalHorasEl.textContent = horasAFormato(totalHoras);
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

      const year = fecha.getFullYear();
      const month = String(fecha.getMonth() + 1).padStart(2, '0');
      const day = String(fecha.getDate()).padStart(2, '0');
      semana.push(`${year}-${month}-${day}`);
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
      await this.updateTableroStats();
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
        const isFirst = false; // Todos cerrados por defecto

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
        const totalExtras = diasSemana.reduce((sum, dia) => sum + (dia.horas_extras || 0), 0);
        const totalTrabajadas = diasSemana.reduce((sum, dia) => sum + (dia.horas_trabajadas || 0), 0);
        const totalRegulares = this.state.proyectoActual.modo_horarios === 'turnos' 
          ? (totalTrabajadas - totalExtras) 
          : totalTrabajadas;
        const totalReales = diasSemana.reduce((sum, dia) => sum + (dia.horas_reales || 0), 0);

        // Crear HTML para el empleado con acordeón
        const seccionHTML = `
          <div class="empleado-section" data-empleado-id="${empleado.id}">
            <div class="empleado-accordion-header ${isFirst ? 'active' : ''}" data-empleado-accordion="${empleado.id}">
              <div class="empleado-header-info">
                <h2>${empleado.nombre}</h2>
                <span class="empleado-hours-badge">${horasAFormato(totalRegulares)}${totalExtras > 0 ? ` <small style="color: #4caf50;">+${horasAFormato(totalExtras)}</small>` : ''}</span>
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
                        ${this.state.proyectoActual.modo_horarios === 'turnos' 
                          ? '<th>Turnos</th>' 
                          : '<th>Entrada</th><th>Salida</th>'}
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
                        ${this.state.proyectoActual.modo_horarios === 'turnos' ? '<td></td>' : '<td></td><td></td>'}
                        <td><strong>${horasAFormato(totalRegulares)}</strong>${totalExtras > 0 ? `<br><small style="color: #4caf50;">+${horasAFormato(totalExtras)} extras</small>` : ''}</td>
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

      // Remover listeners anteriores si existen
      if (this.acordeonHandler) {
        diasColumn.removeEventListener('click', this.acordeonHandler);
      }
      if (this.blurHandler) {
        diasColumn.removeEventListener('blur', this.blurHandler, true);
      }
      if (this.keypressHandler) {
        diasColumn.removeEventListener('keypress', this.keypressHandler);
      }

      // Crear y guardar el handler de acordeones
      this.acordeonHandler = (e: Event) => {
        const target = e.target as HTMLElement;
        const header = target.closest('.empleado-accordion-header') as HTMLElement;

        if (header) {
          e.stopPropagation();
          const empleadoId = header.getAttribute('data-empleado-accordion');

          if (!empleadoId) return;

          // Toggle del acordeón clickeado
          const content = document.querySelector(`[data-empleado-content="${empleadoId}"]`) as HTMLElement;

          if (content) {
            const isActive = header.classList.contains('active');

            if (isActive) {
              header.classList.remove('active');
              content.classList.remove('active');
            } else {
              header.classList.add('active');
              content.classList.add('active');
            }
          }
        }
      };

      // Handler para change de inputs (hora entrada o salida)
      this.blurHandler = async (e: Event) => {
        const target = e.target as HTMLElement;

        // Si es input de hora entrada o salida
        if (target.classList.contains('hora-entrada-input') || target.classList.contains('hora-salida-input')) {
          const input = target as HTMLInputElement;
          const diaId = parseInt(input.dataset.diaId || '0');

          if (!diaId) return;

          // Buscar la fila para obtener ambos valores
          const row = input.closest('tr');
          if (!row) return;

          const horaEntradaInput = row.querySelector('.hora-entrada-input') as HTMLInputElement;
          const horaSalidaInput = row.querySelector('.hora-salida-input') as HTMLInputElement;
          const horasCell = row.querySelector('.horas-calculadas') as HTMLElement;

          const horaEntrada = horaEntradaInput?.value;
          const horaSalida = horaSalidaInput?.value;

          // Solo actualizar si ambos valores están presentes
          if (horaEntrada && horaSalida) {
            try {
              // Animación de cálculo
              if (horasCell) {
                horasCell.classList.add('calculating');
                horasCell.innerHTML = '<span style="opacity: 0.6;">⏳ Calculando...</span>';
              }

              const diaActualizado = await DiaService.updateHorarios(diaId, horaEntrada, horaSalida);

              // Actualizar solo el valor de las horas en el DOM sin recargar todo
              if (horasCell && diaActualizado.horas_trabajadas !== undefined) {
                horasCell.classList.remove('calculating', 'horas-pendiente');
                horasCell.textContent = horasAFormato(diaActualizado.horas_trabajadas);
              }

              // Actualizar totales del empleado sin recargar todo
              const empleadoSection = target.closest('.empleado-section');
              if (empleadoSection) {
                // Recalcular total sumando todas las horas trabajadas del empleado
                const filasEmpleado = empleadoSection.querySelectorAll('tbody tr');
                let totalHoras = 0;
                filasEmpleado.forEach(fila => {
                  const horasCellText = (fila.querySelector('td:nth-child(5)') as HTMLElement)?.textContent || '00:00';
                  if (horasCellText && horasCellText !== '--:--') {
                    const [h, m] = horasCellText.split(':').map(Number);
                    if (!isNaN(h) && !isNaN(m)) {
                      totalHoras += h + (m / 60);
                    }
                  }
                });

                const horasFormateadas = horasAFormato(totalHoras);

                // Actualizar badge en el header del acordeón
                const badgeEl = empleadoSection.querySelector('.empleado-hours-badge') as HTMLElement;
                if (badgeEl) {
                  badgeEl.textContent = horasFormateadas;
                  // Forzar re-render
                  badgeEl.style.display = 'none';
                  badgeEl.offsetHeight; // Trigger reflow
                  badgeEl.style.display = '';
                }

                // Actualizar total en el footer de la tabla
                const footerTotalEl = empleadoSection.querySelector('tfoot td:nth-child(5) strong') as HTMLElement;
                if (footerTotalEl) {
                  footerTotalEl.textContent = horasFormateadas;
                }
              }

              // Actualizar estilos de la fila según tenga horas o no
              if (row && diaActualizado.horas_trabajadas !== undefined) {
                if (diaActualizado.horas_trabajadas > 0) {
                  row.classList.remove('sin-horas');
                  row.classList.add('con-horas');
                } else {
                  row.classList.remove('con-horas');
                  row.classList.add('sin-horas');
                }
              }

              // Actualizar estadísticas globales
              await this.updateTableroStats();

            } catch (error) {
              console.error('❌ Error actualizando horarios:', error);
              // Restaurar estado visual en caso de error
              if (horasCell) {
                horasCell.classList.remove('calculating');
                horasCell.innerHTML = '<span style="color: #ef4444;">❌ Error</span>';
              }
            }
          }
        }
      };

      // Handler para Enter en inputs
      this.keypressHandler = (e: Event) => {
        const target = e.target as HTMLElement;
        if (target.classList.contains('horas-input')) {
          const keyEvent = e as KeyboardEvent;
          if (keyEvent.key === 'Enter') {
            (target as HTMLInputElement).blur();
          }
        }
      };

      // Agregar los event listeners - usar 'change' en lugar de 'blur' para inputs tipo time
      diasColumn.addEventListener('click', this.acordeonHandler);
      diasColumn.addEventListener('change', this.blurHandler, true);
      diasColumn.addEventListener('keypress', this.keypressHandler);

      // Event listener para botones de turnos
      if (this.state.proyectoActual?.modo_horarios === 'turnos') {
        diasColumn.addEventListener('click', (e: Event) => {
          const target = e.target as HTMLElement;
          if (target.classList.contains('btn-ver-turnos')) {
            const diaId = parseInt(target.dataset.diaId || '0');
            const empleadoNombre = target.dataset.empleadoNombre || '';
            const fecha = target.dataset.fecha || '';
            const turnoMananaEntrada = target.dataset.turnoMananaEntrada;
            const turnoMananaSalida = target.dataset.turnoMananaSalida;
            const turnoTardeEntrada = target.dataset.turnoTardeEntrada;
            const turnoTardeSalida = target.dataset.turnoTardeSalida;

            // Importar y usar el handler del modal
            import('./turnos-modal').then(({ TurnosModalHandler }) => {
              TurnosModalHandler.init(this.state.proyectoActual!);
              TurnosModalHandler.abrirModal({
                diaId,
                empleadoNombre,
                fecha,
                turnoMananaEntrada,
                turnoMananaSalida,
                turnoTardeEntrada,
                turnoTardeSalida,
              });
            });
          }
        });
      }

    } catch (error) {
      console.error('Error cargando proyecto con empleados:', error);
    }
  },

  /**
   * Renderiza los días de un empleado
   */
  renderDiasEmpleado(dias: Dia[], mostrarHorasReales: boolean, editable: boolean = true): string {
    const modoTurnos = this.state.proyectoActual?.modo_horarios === 'turnos';
    
    if (!dias.length) {
      return `<tr><td colspan="${mostrarHorasReales ? 6 : 5}" class="text-center">No hay días para mostrar</td></tr>`;
    }

    return dias.map(dia => {
      const fecha = new Date(dia.fecha);
      const horasTrabajadas = horasAFormato(dia.horas_trabajadas || 0);
      const horasReales = horasAFormato(dia.horas_reales || 0);
      const horaEntrada = dia.hora_entrada || '';
      const horaSalida = dia.hora_salida || '';

      // Clase para estilo de fila según tenga horas o no
      const rowClass = (dia.horas_trabajadas || 0) > 0 ? 'con-horas' : 'sin-horas';

      // Modo Turnos
      if (modoTurnos) {
        const tieneTurnos = dia.turno_manana_entrada || dia.turno_tarde_entrada;
        const horasExtras = dia.horas_extras || 0;
        const mostrarExtras = horasExtras > 0;

        return `
          <tr data-dia-id="${dia.id}" class="${rowClass}">
            <td>${formatearFechaSinAnio(dia.fecha)}</td>
            <td>${dia.dia_semana}</td>
            <td class="td-turnos">
              <button 
                class="btn-ver-turnos" 
                data-dia-id="${dia.id}"
                data-empleado-nombre="${this.state.empleados.find(e => e.id === dia.empleado_id)?.nombre || ''}"
                data-fecha="${dia.fecha}"
                data-turno-manana-entrada="${dia.turno_manana_entrada || ''}"
                data-turno-manana-salida="${dia.turno_manana_salida || ''}"
                data-turno-tarde-entrada="${dia.turno_tarde_entrada || ''}"
                data-turno-tarde-salida="${dia.turno_tarde_salida || ''}"
                title="Ver/Editar turnos"
              >
                ${tieneTurnos ? '⏰ Ver Turnos' : '➕ Agregar Turnos'}
              </button>
            </td>
            <td class="td-entrada" style="display: none;">--:--</td>
            <td class="td-salida" style="display: none;">--:--</td>
            <td>
              ${tieneTurnos ? horasAFormato((dia.horas_trabajadas || 0) - horasExtras) : `<span style="opacity: 0.5; font-size: 0.85rem;">--:--</span>`}
              ${mostrarExtras ? `<br><small style="color: #4caf50;">+${horasAFormato(horasExtras)} extras</small>` : ''}
            </td>
            ${mostrarHorasReales ? `<td>${horasReales || '--:--'}</td>` : ''}
          </tr>
        `;
      }

      // Modo Corrido (normal)
      const tieneHorarios = horaEntrada && horaSalida;
      const horasClass = tieneHorarios ? 'horas-calculadas' : 'horas-calculadas horas-pendiente';

      if (editable) {
        return `
          <tr data-dia-id="${dia.id}" class="${rowClass}">
            <td>${formatearFechaSinAnio(dia.fecha)}</td>
            <td>${dia.dia_semana}</td>
            <td class="td-turnos" style="display: none;">--</td>
            <td class="td-entrada">
              <input 
                type="time" 
                class="hora-entrada-input" 
                value="${horaEntrada}" 
                data-dia-id="${dia.id}"
                placeholder="Entrada"
                title="Hora de entrada"
              />
            </td>
            <td class="td-salida">
              <input 
                type="time" 
                class="hora-salida-input" 
                value="${horaSalida}" 
                data-dia-id="${dia.id}"
                placeholder="Salida"
                title="Hora de salida"
              />
            </td>
            <td class="${horasClass}">
              ${tieneHorarios ? horasTrabajadas : `<span style="opacity: 0.5; font-size: 0.85rem;">--:--</span>`}
            </td>
            ${mostrarHorasReales ? `<td>${horasReales || '--:--'}</td>` : ''}
          </tr>
        `;
      } else {
        // Versión solo lectura para modal de visualización
        return `
          <tr data-dia-id="${dia.id}" class="${rowClass}">
            <td>${formatearFechaSinAnio(dia.fecha)}</td>
            <td>${dia.dia_semana}</td>
            <td class="td-turnos" style="display: none;">--</td>
            <td class="td-entrada" style="text-align: center;">${horaEntrada || '<span style="opacity: 0.4;">--:--</span>'}</td>
            <td class="td-salida" style="text-align: center;">${horaSalida || '<span style="opacity: 0.4;">--:--</span>'}</td>
            <td class="${horasClass}">
              ${tieneHorarios ? horasTrabajadas : `<span style="opacity: 0.5; font-size: 0.85rem;">--:--</span>`}
            </td>
            ${mostrarHorasReales ? `<td>${horasReales || '--:--'}</td>` : ''}
          </tr>
        `;
      }
    }).join('');
  },

  /**
   * Exporta PDF de un empleado específico
   */
  async exportarPDFEmpleado(empleadoId: number, empleadoNombre: string): Promise<void> {
    try {
      // Preguntar si quiere exportar semana o mes
      const { value: periodo } = await Swal.fire({
        title: `Exportar PDF - ${empleadoNombre}`,
        text: '¿Qué período deseas exportar?',
        icon: 'question',
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: '📅 Semana Actual',
        denyButtonText: '📆 Mes Completo',
        cancelButtonText: 'Cancelar',
        background: '#0f1419',
        color: '#c8c8c8',
        confirmButtonColor: '#667eea',
        denyButtonColor: '#43e97b',
        cancelButtonColor: '#2d3746',
        iconColor: '#667eea'
      });

      if (!periodo && periodo !== false) return; // Cancelado

      const esSemana = periodo === true; // true = confirmButton (Semana), false = denyButton (Mes)

      // Mostrar loading
      Swal.fire({
        title: 'Generando PDF...',
        text: 'Por favor espera',
        allowOutsideClick: false,
        showConfirmButton: false,
        background: '#0f1419',
        color: '#c8c8c8',
        didOpen: () => {
          Swal.showLoading();
        }
      });

      if (!this.state.proyectoActual) return;

      // Obtener días según el período seleccionado
      let dias: Dia[];
      let periodoTexto: string;

      if (esSemana) {
        // Semana actual
        const semanaFechas = this.getSemanActual();
        const todosDias = await DiaService.getDiasMes(
          this.state.proyectoActual.id,
          this.state.anioActual,
          this.state.mesActual,
          empleadoId
        );
        dias = todosDias.filter((dia) => {
          const diaFecha = new Date(dia.fecha).toISOString().split('T')[0];
          return semanaFechas.includes(diaFecha);
        });
        periodoTexto = 'Semana Actual';
      } else {
        // Mes completo
        dias = await DiaService.getDiasMes(
          this.state.proyectoActual.id,
          this.state.anioActual,
          this.state.mesActual,
          empleadoId
        );
        const mesNombre = MESES_ES[this.state.mesActual as keyof typeof MESES_ES];
        periodoTexto = `${mesNombre} ${this.state.anioActual}`;
      }

      // Generar PDF usando la utilidad
      const { generateEmpleadoPDF } = await import('../utils/pdf');
      await generateEmpleadoPDF(
        empleadoNombre,
        this.state.proyectoActual,
        periodoTexto,
        dias
      );

      // Cerrar loading y mostrar éxito
      Swal.fire({
        icon: 'success',
        title: '¡PDF Generado!',
        text: 'El archivo se ha descargado correctamente',
        showConfirmButton: false,
        timer: 2000,
        background: '#0f1419',
        color: '#c8c8c8',
        iconColor: '#43e97b'
      });
    } catch (error) {
      console.error('Error generando PDF:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo generar el PDF',
        background: '#0f1419',
        color: '#c8c8c8',
        iconColor: '#ef4444',
        confirmButtonColor: '#ef4444'
      });
    }
  },

  async mostrarModalConfiguracion(): Promise<void> {
    const proyecto = this.state.proyectoActual;
    if (!proyecto) return;

    const { value: formValues } = await Swal.fire({
      title: 'Configuración del Proyecto',
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
              <span style="font-size: 15px; color: #c8c8c8;">Activar columna de Horas Reales</span>
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
        // Manejar cambio de modo de horarios
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

        // Calcular horario_inicio y horario_fin automáticamente desde los turnos
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

    if (formValues && this.state.proyectoActual) {
      try {
        await ProyectoService.updateConfiguracion(
          this.state.proyectoActual.id,
          formValues
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
          <h4>${tarea.titulo}</h4>
          <small>${tarea.horas || '00:00'} horas</small>
        </div>
      `).join('');

      // Agregar listeners a cada elemento individual
      tareasList.querySelectorAll('.tarea-item').forEach((element) => {
        // Click simple: mostrar detalles
        element.addEventListener('click', (e: Event) => {
          if ((e as PointerEvent).detail === 1) {
            const tareaId = parseInt(element.getAttribute('data-tarea-id') || '0');
            const tarea = tareas.find((t: any) => t.id === tareaId);

            if (tarea) {
              // Disparar evento personalizado para que sea manejado en el .astro
              const event = new CustomEvent('view-tarea-empleados', { detail: { tarea } });
              document.dispatchEvent(event);
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
      const modoTurnos = this.state.proyectoActual.modo_horarios === 'turnos';
      
      if (thHorasReales) {
        thHorasReales.style.display = mostrarHorasReales ? '' : 'none';
      }
      if (tdTotalReales) {
        tdTotalReales.style.display = mostrarHorasReales ? '' : 'none';
      }
      
      // Actualizar headers según modo
      const thTurnos = document.getElementById('empleado-th-turnos');
      const thEntrada = document.getElementById('empleado-th-entrada');
      const thSalida = document.getElementById('empleado-th-salida');
      
      const tdTurnosFooter = document.querySelectorAll('.td-turnos-footer');
      const tdEntradaFooter = document.querySelectorAll('.td-entrada-footer');
      const tdSalidaFooter = document.querySelectorAll('.td-salida-footer');
      
      if (modoTurnos) {
        if (thTurnos) thTurnos.style.display = '';
        if (thEntrada) thEntrada.style.display = 'none';
        if (thSalida) thSalida.style.display = 'none';
        tdTurnosFooter.forEach(td => (td as HTMLElement).style.display = '');
        tdEntradaFooter.forEach(td => (td as HTMLElement).style.display = 'none');
        tdSalidaFooter.forEach(td => (td as HTMLElement).style.display = 'none');
      } else {
        if (thTurnos) thTurnos.style.display = 'none';
        if (thEntrada) thEntrada.style.display = '';
        if (thSalida) thSalida.style.display = '';
        tdTurnosFooter.forEach(td => (td as HTMLElement).style.display = 'none');
        tdEntradaFooter.forEach(td => (td as HTMLElement).style.display = '');
        tdSalidaFooter.forEach(td => (td as HTMLElement).style.display = '');
      }

      // Cargar días del mes completo
      const dias = await DiaService.getDiasMes(
        this.state.proyectoActual.id,
        this.state.anioActual,
        this.state.mesActual,
        empleadoId
      );

      // Calcular totales
      const sumaHorasExtras = dias.reduce((sum, dia) => sum + (dia.horas_extras || 0), 0);
      const sumaHorasTrabajadas = dias.reduce((sum, dia) => sum + (dia.horas_trabajadas || 0), 0);
      const sumaHorasRegulares = modoTurnos ? (sumaHorasTrabajadas - sumaHorasExtras) : sumaHorasTrabajadas;
      const sumaHorasReales = dias.reduce((sum, dia) => sum + (dia.horas_reales || 0), 0);

      // Renderizar días (ahora editable en el modal también)
      tbody.innerHTML = this.renderDiasEmpleado(dias, mostrarHorasReales, true);

      // Aplicar visibilidad a las celdas del tbody según el modo
      const tdTurnosBody = tbody.querySelectorAll('.td-turnos');
      const tdEntradaBody = tbody.querySelectorAll('.td-entrada');
      const tdSalidaBody = tbody.querySelectorAll('.td-salida');
      
      if (modoTurnos) {
        tdTurnosBody.forEach(td => (td as HTMLElement).style.display = '');
        tdEntradaBody.forEach(td => (td as HTMLElement).style.display = 'none');
        tdSalidaBody.forEach(td => (td as HTMLElement).style.display = 'none');
      } else {
        tdTurnosBody.forEach(td => (td as HTMLElement).style.display = 'none');
        tdEntradaBody.forEach(td => (td as HTMLElement).style.display = '');
        tdSalidaBody.forEach(td => (td as HTMLElement).style.display = '');
      }

      // Actualizar totales (mostrar horas regulares, sin extras)
      if (totalTrabajadas) {
        totalTrabajadas.textContent = horasAFormato(sumaHorasRegulares);
      }
      if (totalReales) {
        totalReales.textContent = horasAFormato(sumaHorasReales);
      }

      // Mostrar modal
      modal.style.display = 'flex';

      // Event listener para botones de turnos en el modal
      if (modoTurnos) {
        tbody.addEventListener('click', (e: Event) => {
          const target = e.target as HTMLElement;
          if (target.classList.contains('btn-ver-turnos')) {
            const diaId = parseInt(target.dataset.diaId || '0');
            const empleadoNombreBtn = target.dataset.empleadoNombre || '';
            const fecha = target.dataset.fecha || '';
            const turnoMananaEntrada = target.dataset.turnoMananaEntrada;
            const turnoMananaSalida = target.dataset.turnoMananaSalida;
            const turnoTardeEntrada = target.dataset.turnoTardeEntrada;
            const turnoTardeSalida = target.dataset.turnoTardeSalida;

            // Importar y usar el handler del modal de turnos
            import('./turnos-modal').then(({ TurnosModalHandler }) => {
              TurnosModalHandler.init(this.state.proyectoActual!);
              TurnosModalHandler.abrirModal({
                diaId,
                empleadoNombre: empleadoNombreBtn,
                fecha,
                turnoMananaEntrada,
                turnoMananaSalida,
                turnoTardeEntrada,
                turnoTardeSalida,
              });
            });
          }
        });
      }

      // Agregar event listeners para los inputs del modal (usar 'change' en lugar de 'blur')
      const modalChangeHandler = async (e: Event) => {
        const target = e.target as HTMLElement;

        if (target.classList.contains('hora-entrada-input') || target.classList.contains('hora-salida-input')) {
          const input = target as HTMLInputElement;
          const diaId = parseInt(input.dataset.diaId || '0');

          if (!diaId) return;

          const row = input.closest('tr');
          if (!row) return;

          const horaEntradaInput = row.querySelector('.hora-entrada-input') as HTMLInputElement;
          const horaSalidaInput = row.querySelector('.hora-salida-input') as HTMLInputElement;
          const horasCell = row.querySelector('.horas-calculadas') as HTMLElement;

          const horaEntrada = horaEntradaInput?.value;
          const horaSalida = horaSalidaInput?.value;

          if (horaEntrada && horaSalida) {
            try {
              if (horasCell) {
                horasCell.classList.add('calculating');
                horasCell.innerHTML = '<span style="opacity: 0.6;">⏳ Calculando...</span>';
              }

              const diaActualizado = await DiaService.updateHorarios(diaId, horaEntrada, horaSalida);

              // Actualizar solo el valor de las horas en el DOM sin recargar todo
              if (horasCell && diaActualizado.horas_trabajadas !== undefined) {
                horasCell.classList.remove('calculating', 'horas-pendiente');
                horasCell.textContent = horasAFormato(diaActualizado.horas_trabajadas);
              }

              // Recalcular totales sumando las celdas actuales sin recargar
              const filas = tbody.querySelectorAll('tr');
              let sumaTrabajadasActualizada = 0;
              let sumaRealesActualizada = 0;

              filas.forEach(fila => {
                const horasTrabajadas = (fila.querySelector('.horas-calculadas') as HTMLElement)?.textContent || '00:00';
                const horasReales = (fila.querySelector('td:nth-child(6)') as HTMLElement)?.textContent || '00:00';

                const [ht, mt] = horasTrabajadas.split(':').map(Number);
                const [hr, mr] = horasReales.split(':').map(Number);

                sumaTrabajadasActualizada += ht + (mt / 60);
                sumaRealesActualizada += hr + (mr / 60);
              });

              if (totalTrabajadas) totalTrabajadas.textContent = horasAFormato(sumaTrabajadasActualizada);
              if (totalReales) totalReales.textContent = horasAFormato(sumaRealesActualizada);

              // Actualizar el acordeón principal sin recargar todo
              const acordeonHeader = document.querySelector(`[data-empleado-accordion="${empleadoId}"]`);
              if (acordeonHeader) {
                const totalHorasEl = acordeonHeader.querySelector('.empleado-horas-total');
                if (totalHorasEl) {
                  totalHorasEl.textContent = horasAFormato(sumaTrabajadasActualizada);
                }
              }

              // Actualizar estadísticas globales
              await this.updateTableroStats();
            } catch (error) {
              console.error('❌ [Modal] Error actualizando horarios:', error);
              if (horasCell) {
                horasCell.classList.remove('calculating');
                horasCell.innerHTML = '<span style="color: #ef4444;">❌ Error</span>';
              }
            }
          }
        }
      };

      tbody.addEventListener('change', modalChangeHandler, true);

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
