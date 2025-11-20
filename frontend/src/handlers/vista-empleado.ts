/**
 * Handler para la vista del empleado
 * Vista que ve un usuario cuando accede a un tablero donde es empleado
 */

import Swal from 'sweetalert2';
import { DiaService } from '../services/dia';
import { TareaService } from '../services/tarea';
import type { Dia, Tarea, Empleado, Proyecto } from '../types';
import { horasAFormato, MESES_ES } from '../utils/formatters';

export const VistaEmpleadoHandler = {
  state: {
    empleadoActual: null as Empleado | null,
    proyecto: null as Proyecto | null,
    dias: [] as Dia[],
    tareasAsignadas: [] as Tarea[],
    mesActual: new Date().getMonth() + 1,
    anioActual: new Date().getFullYear(),
  },

  /**
   * Inicializar vista del empleado
   */
  async inicializar(empleadoId: number, proyectoId: number): Promise<void> {
    try {
      // Cargar datos del empleado y proyecto
      await this.cargarDatosEmpleado(empleadoId, proyectoId);
      await this.cargarDiasMes();
      await this.cargarTareasAsignadas();
      
      this.renderizarVista();
    } catch (error) {
      console.error('Error inicializando vista empleado:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo cargar la información del empleado',
        background: '#0f1419',
        color: '#c8c8c8',
      });
    }
  },

  /**
   * Cargar datos del empleado
   */
  async cargarDatosEmpleado(empleadoId: number, proyectoId: number): Promise<void> {
    // TODO: Implementar servicio para obtener datos del empleado
    // const empleado = await EmpleadosService.getEmpleado(empleadoId);
    // const proyecto = await ProyectosService.getProyecto(proyectoId);
    // this.state.empleadoActual = empleado;
    // this.state.proyecto = proyecto;
  },

  /**
   * Cargar días del mes actual
   */
  async cargarDiasMes(): Promise<void> {
    if (!this.state.empleadoActual || !this.state.proyecto) return;

    try {
      const dias = await DiaService.getDiasMes(
        this.state.proyecto.id,
        this.state.anioActual,
        this.state.mesActual
      );
      
      // Filtrar solo los días del empleado actual
      this.state.dias = dias.filter(
        dia => dia.empleado_id === this.state.empleadoActual?.id
      );
    } catch (error) {
      console.error('Error cargando días:', error);
    }
  },

  /**
   * Cargar tareas asignadas al empleado
   */
  async cargarTareasAsignadas(): Promise<void> {
    if (!this.state.proyecto) return;

    try {
      const todasLasTareas = await TareaService.getTareasProyecto(this.state.proyecto.id);
      
      // Filtrar tareas que tienen días asignados a este empleado
      this.state.tareasAsignadas = todasLasTareas.filter(tarea =>
        tarea.dias?.some(dia => dia.empleado_id === this.state.empleadoActual?.id)
      );
    } catch (error) {
      console.error('Error cargando tareas:', error);
    }
  },

  /**
   * Renderizar la vista del empleado
   */
  renderizarVista(): void {
    const container = document.getElementById('vista-empleado-container');
    if (!container) return;

    const { proyecto, empleadoActual, dias, tareasAsignadas } = this.state;
    if (!proyecto || !empleadoActual) return;

    const totalHorasTrabajadas = dias.reduce((sum, dia) => sum + (dia.horas_trabajadas || 0), 0);
    const totalHorasReales = dias.reduce((sum, dia) => sum + (dia.horas_reales || 0), 0);
    const diasTrabajados = dias.filter(dia => dia.horas_trabajadas && dia.horas_trabajadas > 0).length;

    container.innerHTML = `
      <div class="vista-empleado">
        <!-- Header Personal -->
        <div class="empleado-header">
          <div class="empleado-info">
            <div class="empleado-avatar">
              ${empleadoActual.nombre.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2>${empleadoActual.nombre}</h2>
              <p class="empleado-proyecto">${proyecto.nombre}</p>
            </div>
          </div>
          <div class="empleado-stats">
            <div class="stat-card">
              <div class="stat-icon">📅</div>
              <div class="stat-content">
                <span class="stat-value">${diasTrabajados}</span>
                <span class="stat-label">Días trabajados</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">⏱️</div>
              <div class="stat-content">
                <span class="stat-value">${horasAFormato(totalHorasTrabajadas)}</span>
                <span class="stat-label">Horas trabajadas</span>
              </div>
            </div>
            ${proyecto.horas_reales_activas ? `
              <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-content">
                  <span class="stat-value">${horasAFormato(totalHorasReales)}</span>
                  <span class="stat-label">Horas reales</span>
                </div>
              </div>
            ` : ''}
          </div>
        </div>

        <!-- Tabs -->
        <div class="empleado-tabs">
          <button class="tab-btn active" data-tab="mis-horas">📋 Mis Horas</button>
          <button class="tab-btn" data-tab="mis-tareas">✓ Mis Tareas</button>
          <button class="tab-btn" data-tab="resumen">📊 Resumen</button>
        </div>

        <!-- Contenido Tabs -->
        <div class="tab-content-container">
          <!-- Tab: Mis Horas -->
          <div class="tab-content active" id="tab-mis-horas">
            ${this.renderizarTablaDias()}
          </div>

          <!-- Tab: Mis Tareas -->
          <div class="tab-content" id="tab-mis-tareas">
            ${this.renderizarTareasAsignadas()}
          </div>

          <!-- Tab: Resumen -->
          <div class="tab-content" id="tab-resumen">
            ${this.renderizarResumen()}
          </div>
        </div>
      </div>
    `;

    this.attachEventListeners();
  },

  /**
   * Renderizar tabla de días
   */
  renderizarTablaDias(): string {
    const { dias, proyecto } = this.state;
    const modoTurnos = proyecto?.modo_horarios === 'turnos';

    if (dias.length === 0) {
      return `
        <div class="empty-state">
          <p>📭 No hay registros de horas para este mes</p>
        </div>
      `;
    }

    const filasHTML = dias.map(dia => {
      const fecha = new Date(dia.fecha);
      const diaSemana = fecha.toLocaleDateString('es-ES', { weekday: 'short' });
      const fechaFormato = fecha.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' });

      return `
        <tr class="dia-row ${dia.horas_trabajadas ? '' : 'sin-horas'}">
          <td>${fechaFormato}</td>
          <td>${diaSemana}</td>
          ${modoTurnos ? `<td>${dia.turno || '-'}</td>` : ''}
          <td>${dia.hora_entrada || '-'}</td>
          <td>${dia.hora_salida || '-'}</td>
          <td class="horas-cell">${dia.horas_trabajadas ? horasAFormato(dia.horas_trabajadas) : '-'}</td>
          ${proyecto?.horas_reales_activas ? `
            <td class="horas-cell">${dia.horas_reales ? horasAFormato(dia.horas_reales) : '-'}</td>
          ` : ''}
          <td>
            ${dia.horas_trabajadas ? `
              <button class="btn-icon" onclick="VistaEmpleadoHandler.verDetalleDia(${dia.id})" title="Ver detalle">
                👁️
              </button>
            ` : ''}
          </td>
        </tr>
      `;
    }).join('');

    return `
      <div class="tabla-container">
        <table class="tabla-dias">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Día</th>
              ${modoTurnos ? '<th>Turno</th>' : ''}
              <th>Entrada</th>
              <th>Salida</th>
              <th>Horas Trabajadas</th>
              ${proyecto?.horas_reales_activas ? '<th>Horas Reales</th>' : ''}
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            ${filasHTML}
          </tbody>
        </table>
      </div>
    `;
  },

  /**
   * Renderizar tareas asignadas
   */
  renderizarTareasAsignadas(): string {
    const { tareasAsignadas } = this.state;

    if (tareasAsignadas.length === 0) {
      return `
        <div class="empty-state">
          <p>📋 No tienes tareas asignadas en este proyecto</p>
        </div>
      `;
    }

    const tareasHTML = tareasAsignadas.map(tarea => {
      const diasAsignados = tarea.dias?.filter(
        dia => dia.empleado_id === this.state.empleadoActual?.id
      ) || [];

      return `
        <div class="tarea-card">
          <div class="tarea-header">
            <h3>${tarea.titulo}</h3>
            <span class="tarea-dias-badge">${diasAsignados.length} días</span>
          </div>
          ${tarea.detalle ? `<p class="tarea-detalle">${tarea.detalle}</p>` : ''}
          ${tarea.que_falta ? `
            <div class="tarea-falta">
              <strong>⚠️ Qué falta:</strong>
              <p>${tarea.que_falta}</p>
            </div>
          ` : ''}
          <div class="tarea-dias">
            <strong>Días asignados:</strong>
            <div class="dias-chips">
              ${diasAsignados.map(dia => {
                const fecha = new Date(dia.fecha);
                return `<span class="dia-chip">${fecha.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })}</span>`;
              }).join('')}
            </div>
          </div>
        </div>
      `;
    }).join('');

    return `<div class="tareas-list">${tareasHTML}</div>`;
  },

  /**
   * Renderizar resumen mensual
   */
  renderizarResumen(): string {
    const { dias, proyecto } = this.state;
    
    const totalHoras = dias.reduce((sum, dia) => sum + (dia.horas_trabajadas || 0), 0);
    const totalReales = dias.reduce((sum, dia) => sum + (dia.horas_reales || 0), 0);
    const diasConHoras = dias.filter(dia => dia.horas_trabajadas && dia.horas_trabajadas > 0);
    const promedioDiario = diasConHoras.length > 0 ? totalHoras / diasConHoras.length : 0;

    // Agrupar por semana
    const semanas: { [key: number]: Dia[] } = {};
    dias.forEach(dia => {
      const fecha = new Date(dia.fecha);
      const semana = Math.ceil(fecha.getDate() / 7);
      if (!semanas[semana]) semanas[semana] = [];
      semanas[semana].push(dia);
    });

    const semanasHTML = Object.entries(semanas).map(([numSemana, diasSemana]) => {
      const horasSemana = diasSemana.reduce((sum, dia) => sum + (dia.horas_trabajadas || 0), 0);
      return `
        <div class="semana-resumen">
          <span class="semana-label">Semana ${numSemana}</span>
          <span class="semana-horas">${horasAFormato(horasSemana)}</span>
        </div>
      `;
    }).join('');

    return `
      <div class="resumen-container">
        <div class="resumen-stats">
          <div class="stat-box">
            <h4>Total del Mes</h4>
            <div class="stat-big">${horasAFormato(totalHoras)}</div>
            <p>Horas trabajadas</p>
          </div>
          ${proyecto?.horas_reales_activas ? `
            <div class="stat-box">
              <h4>Horas Reales</h4>
              <div class="stat-big">${horasAFormato(totalReales)}</div>
              <p>Registradas</p>
            </div>
          ` : ''}
          <div class="stat-box">
            <h4>Promedio Diario</h4>
            <div class="stat-big">${horasAFormato(promedioDiario)}</div>
            <p>Por día trabajado</p>
          </div>
          <div class="stat-box">
            <h4>Días Trabajados</h4>
            <div class="stat-big">${diasConHoras.length}</div>
            <p>De ${dias.length} días</p>
          </div>
        </div>

        <div class="resumen-semanal">
          <h4>Resumen Semanal</h4>
          ${semanasHTML}
        </div>
      </div>
    `;
  },

  /**
   * Ver detalle de un día
   */
  async verDetalleDia(diaId: number): Promise<void> {
    const dia = this.state.dias.find(d => d.id === diaId);
    if (!dia) return;

    const fecha = new Date(dia.fecha);
    const fechaFormato = fecha.toLocaleDateString('es-ES', { 
      weekday: 'long', 
      day: '2-digit', 
      month: 'long', 
      year: 'numeric' 
    });

    await Swal.fire({
      title: `Detalle del Día`,
      html: `
        <div style="text-align: left; padding: 10px;">
          <p style="color: #9ca3af; margin-bottom: 20px;">${fechaFormato}</p>
          
          ${dia.turno ? `
            <div style="margin-bottom: 15px;">
              <strong style="color: #c8c8c8;">Turno:</strong>
              <span style="color: #9ca3af; margin-left: 10px;">${dia.turno}</span>
            </div>
          ` : ''}
          
          <div style="margin-bottom: 15px;">
            <strong style="color: #c8c8c8;">Horario:</strong>
            <span style="color: #9ca3af; margin-left: 10px;">${dia.hora_entrada || '-'} - ${dia.hora_salida || '-'}</span>
          </div>
          
          <div style="margin-bottom: 15px;">
            <strong style="color: #c8c8c8;">Horas Trabajadas:</strong>
            <span style="color: #667eea; margin-left: 10px; font-size: 1.2em;">${horasAFormato(dia.horas_trabajadas || 0)}</span>
          </div>
          
          ${dia.horas_reales ? `
            <div style="margin-bottom: 15px;">
              <strong style="color: #c8c8c8;">Horas Reales:</strong>
              <span style="color: #10b981; margin-left: 10px; font-size: 1.2em;">${horasAFormato(dia.horas_reales)}</span>
            </div>
          ` : ''}

          ${dia.observaciones ? `
            <div style="margin-top: 20px; padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
              <strong style="color: #c8c8c8;">Observaciones:</strong>
              <p style="color: #9ca3af; margin-top: 8px;">${dia.observaciones}</p>
            </div>
          ` : ''}
        </div>
      `,
      confirmButtonText: 'Cerrar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#667eea',
      width: '500px',
    });
  },

  /**
   * Attach event listeners
   */
  attachEventListeners(): void {
    // Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        const tab = target.getAttribute('data-tab');
        
        tabBtns.forEach(b => b.classList.remove('active'));
        target.classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(content => {
          content.classList.remove('active');
        });
        document.getElementById(`tab-${tab}`)?.classList.add('active');
      });
    });
  },

  /**
   * Cambiar mes
   */
  async cambiarMes(mes: number, anio: number): Promise<void> {
    this.state.mesActual = mes;
    this.state.anioActual = anio;
    await this.cargarDiasMes();
    this.renderizarVista();
  },
};

// Exponer globalmente para ser usado desde el HTML
(window as any).VistaEmpleadoHandler = VistaEmpleadoHandler;
