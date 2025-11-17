/**
 * Proyecto Details Page Handlers - Lógica separada del .astro
 */

import type { Proyecto, Dia, Usuario } from '../types';
import { ProyectoService } from '../services/proyecto';
import { DiaService } from '../services/dia';
import { TareaService } from '../services/tarea';
import { AuthService } from '../services/auth';
import { querySelector, querySelectorAll } from '../utils/dom';
import { showErrorModal, showLoadingModal, closeModal } from '../utils/modals';
import { MESES_ES, horasAFormato } from '../utils/formatters';

export interface ProyectoDetailState {
  proyectoActual: Proyecto | null;
  diasActuales: Dia[];
  tareasActuales: any[];
  usuarioActual: Usuario | null;
  mesActual: number;
  anioActual: number;
}

const state: ProyectoDetailState = {
  proyectoActual: null,
  diasActuales: [],
  tareasActuales: [],
  usuarioActual: null,
  mesActual: new Date().getMonth() + 1,
  anioActual: new Date().getFullYear(),
};

// ============================================================
// Helpers para calcular horas
// ============================================================

/**
 * Determina si debe mostrar horas reales o estimadas
 */
function useHorasReales(): boolean {
  return state.usuarioActual?.usar_horas_reales || false;
}

/**
 * Obtiene las horas a mostrar según configuración del usuario
 */
function getHorasAMostrar(dia: Dia): number {
  if (useHorasReales()) {
    return dia.horas_reales || 0;
  }
  return dia.horas_trabajadas || 0;
}

/**
 * Calcula las horas de una tarea según los días asignados y configuración
 */
function calcularHorasTarea(tarea: any): string {
  if (!tarea.dias || tarea.dias.length === 0) {
    return '00:00';
  }

  let totalHoras = 0;

  tarea.dias.forEach((dia: Dia) => {
    if (useHorasReales()) {
      totalHoras += dia.horas_reales || 0;
    } else {
      totalHoras += dia.horas_trabajadas || 0;
    }
  });

  return horasAFormato(totalHoras);
}

/**
 * Obtiene la semana actual en formato YYYY-MM-DD
 * Respeta la preferencia del usuario para el día de inicio de semana
 */
function getSemanActual(): string[] {
  const hoy = new Date();
  const diaActual = hoy.getDay(); // 0 = Domingo, 1 = Lunes, ..., 6 = Sábado
  const diaInicioSemana = state.usuarioActual?.dia_inicio_semana || 0; // 0 = Domingo, 1 = Lunes
  
  // Calcular el primer día de la semana
  let diasAtras = diaActual - diaInicioSemana;
  if (diasAtras < 0) {
    diasAtras += 7;
  }
  
  const primDia = hoy.getDate() - diasAtras;
  const semana = [];

  for (let i = primDia; i <= primDia + 6; i++) {
    const fecha = new Date(hoy.getFullYear(), hoy.getMonth(), i);
    semana.push(fecha.toISOString().split('T')[0]);
  }

  return semana;
}

// ============================================================
// Carga de datos
// ============================================================

/**
 * Carga el usuario actual
 */
export async function loadCurrentUser(): Promise<void> {
  try {
    state.usuarioActual = await AuthService.getCurrentUser();
  } catch (error) {
    console.error('Error cargando usuario:', error);
  }
}

/**
 * Carga el proyecto
 */
export async function loadProyecto(): Promise<void> {
  try {
    await loadCurrentUser();

    const path = window.location.pathname;
    const proyectoId = parseInt(path.split('/').pop() || '0');

    if (!proyectoId) {
      window.location.href = '/proyectos';
      return;
    }

    state.proyectoActual = await ProyectoService.getProyecto(proyectoId);

    if (!state.proyectoActual) {
      window.location.href = '/proyectos';
      return;
    }

    // Actualizar UI
    updateProjectHeader();
    updateProjectCard();

    // Establecer mes y año
    state.mesActual = state.proyectoActual.mes;
    state.anioActual = state.proyectoActual.anio;

    // Cargar datos
    await loadDias();
    await loadTareas();
    updateTotalPanel();
  } catch (error) {
    console.error('Error cargando proyecto:', error);
    showErrorModal('Error', 'No se pudo cargar el proyecto');
  }
}

/**
 * Verifica si un mes es válido para mostrar
 */
function getMesStatus(): 'futuro' | 'activo' | 'pasado' {
  const hoy = new Date();
  const mesActual = hoy.getMonth() + 1; // 1-12
  const anioActual = hoy.getFullYear();

  if (state.anioActual > anioActual) return 'futuro';
  if (state.anioActual < anioActual) return 'pasado';
  
  // Mismo año
  if (state.mesActual > mesActual) return 'futuro';
  if (state.mesActual < mesActual) return 'pasado';
  
  return 'activo';
}

/**
 * Oculta o muestra el row de totales
 */
function toggleTotalsRow(show: boolean) {
  const tfoot = document.querySelector('table tfoot') as HTMLTableSectionElement | null;
  if (tfoot) {
    tfoot.style.display = show ? '' : 'none';
  }
}

/**
 * Carga los días del mes actual
 */
export async function loadDias(): Promise<void> {
  try {
    if (!state.proyectoActual) return;

    // Verificar estado del mes
    const mesStatus = getMesStatus();
    const diasTbody = document.querySelector('#dias-tbody');
    const mesDiasTbody = document.querySelector('#mes-dias-tbody');

    if (mesStatus !== 'activo') {
      // Mostrar mensaje en lugar de tabla
      const esFuturo = mesStatus === 'futuro';
      const mensaje = esFuturo 
        ? 'Mes aún no iniciado' 
        : 'Mes terminado';
      const icono = esFuturo ? '📅' : '✓';
      
      const html = `
        <tr>
          <td colspan="4" class="mes-message-row">
            <div class="mes-message">
              <span class="mes-icon">${icono}</span>
              <span class="mes-text">${mensaje}</span>
            </div>
          </td>
        </tr>
      `;

      if (diasTbody) diasTbody.innerHTML = html;
      if (mesDiasTbody) mesDiasTbody.innerHTML = html;
      
      // Ocultar totales cuando el mes no está activo
      toggleTotalsRow(false);
      return;
    }

    // Mostrar totales cuando el mes está activo
    toggleTotalsRow(true);

    state.diasActuales = await DiaService.getDiasMes(
      state.proyectoActual.id,
      state.anioActual,
      state.mesActual
    );

    // Obtener días de la semana actual
    const semanaFechas = getSemanActual();
    const diasSemana = state.diasActuales.filter((dia) => {
      const diaFecha = new Date(dia.fecha).toISOString().split('T')[0];
      return semanaFechas.includes(diaFecha);
    });

    renderTablaDias(diasSemana, 'dias-tbody', 'total-trabajadas', 'total-reales');
    renderTablaDias(state.diasActuales, 'mes-dias-tbody', 'mes-total-trabajadas', 'mes-total-reales');
  } catch (error) {
    console.error('Error cargando días:', error);
  }
}

/**
 * Carga las tareas
 */
export async function loadTareas(): Promise<void> {
  try {
    if (!state.proyectoActual) return;

    state.tareasActuales = await TareaService.getTareasProyecto(state.proyectoActual.id);

    const listEl = querySelector<HTMLElement>('#tareas-list');
    const countEl = querySelector<HTMLElement>('#tareas-count');

    if (!listEl) return;

    if (state.tareasActuales.length === 0) {
      listEl.innerHTML = '<div class="empty-tareas"><p>📭 Sin tareas aún</p></div>';
    } else {
      listEl.innerHTML = state.tareasActuales
        .map((tarea) => renderTareaItem(tarea))
        .join('');

      // Agregar event listeners
      attachTareaListeners();
    }

    if (countEl) {
      countEl.textContent = state.tareasActuales.length.toString();
    }
  } catch (error) {
    console.error('Error cargando tareas:', error);
  }
}

// ============================================================
// Renderizado de elementos
// ============================================================

/**
 * Renderiza un item de tarea
 */
function renderTareaItem(tarea: any): string {
  let horasAMostrar = tarea.horas || '00:00';

  if (!horasAMostrar || horasAMostrar === '') {
    horasAMostrar = calcularHorasTarea(tarea);
  }

  return `
    <div class="tarea-item" data-tarea-id="${tarea.id}">
      <h4>${tarea.titulo}</h4>
      <small>${horasAMostrar} horas</small>
    </div>
  `;
}

/**
 * Renderiza tabla de días con lógica de horas reales
 */
function renderTablaDias(
  dias: Dia[],
  tbodyId: string,
  totalTrabId: string,
  totalRealId: string
): void {
  const tbody = querySelector<HTMLTableSectionElement>(`#${tbodyId}`);
  if (!tbody) return;

  tbody.innerHTML = '';

  let totalTrabajadas = 0;
  let totalReales = 0;

  dias.forEach((dia) => {
    const horasAMostrar = getHorasAMostrar(dia);
    totalTrabajadas += dia.horas_trabajadas || 0;
    totalReales += horasAMostrar;

    const row = document.createElement('tr');
    const fecha = new Date(dia.fecha);
    
    // Agregar clase según las horas trabajadas
    if ((dia.horas_trabajadas || 0) === 0) {
      row.classList.add('dia-sin-horas');
    } else {
      row.classList.add('dia-con-horas');
    }

    const columnasExtras = useHorasReales()
      ? `<td title="Horas Reales"><strong>${horasAFormato(horasAMostrar)}</strong></td>`
      : '<td></td>';

    row.innerHTML = `
      <td>${fecha.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })}</td>
      <td>${dia.dia_semana}</td>
      <td>
        <input type="text" class="horas-input horas-trabajadas" 
          data-dia-id="${dia.id}" 
          value="${horasAFormato(dia.horas_trabajadas || 0)}" />
      </td>
      ${columnasExtras}
    `;

    // Marcar columna Horas Reales como oculta si no se usa
    if (!useHorasReales()) {
      const lastTd = row.lastElementChild as HTMLElement;
      if (lastTd) lastTd.style.display = 'none';
    }

    // Event listener para cambios
    const input = row.querySelector<HTMLInputElement>('.horas-trabajadas');
    if (input) {
      input.addEventListener('change', () => updateHoras(dia.id, input.value));
    }

    tbody.appendChild(row);
  });

  // Actualizar visibilidad de columnas
  updateColumnVisibility();

  // Actualizar totales
  updateTotals(totalTrabId, totalRealId, totalTrabajadas, totalReales);
}

/**
 * Actualiza la visibilidad de columnas de horas reales
 */
function updateColumnVisibility(): void {
  const thRealHeader = querySelector<HTMLElement>('#th-horas-reales');
  const tdTotalRealFooter = querySelector<HTMLElement>('#td-total-reales');

  if (thRealHeader) {
    thRealHeader.style.display = useHorasReales() ? '' : 'none';
  }
  if (tdTotalRealFooter) {
    tdTotalRealFooter.style.display = useHorasReales() ? '' : 'none';
  }
}

/**
 * Actualiza los elementos de totales
 */
function updateTotals(
  totalTrabId: string,
  totalRealId: string,
  totalTrabajadas: number,
  totalReales: number
): void {
  const totalTrabEl = querySelector<HTMLElement>(`#${totalTrabId}`);
  const totalRealEl = querySelector<HTMLElement>(`#${totalRealId}`);

  if (totalTrabEl) {
    totalTrabEl.textContent = horasAFormato(totalTrabajadas);
  }

  if (totalRealEl) {
    totalRealEl.textContent = horasAFormato(totalReales);
  }
}

/**
 * Actualiza el panel de totales general
 */
function updateTotalPanel(): void {
  if (!state.proyectoActual) return;

  let totalReales = 0;
  state.diasActuales.forEach((dia) => {
    totalReales += getHorasAMostrar(dia);
  });

  const panelEl = querySelector<HTMLElement>('#panel-total-reales');
  if (panelEl) {
    panelEl.textContent = horasAFormato(totalReales);
  }
}

/**
 * Actualiza el header del proyecto
 */
function updateProjectHeader(): void {
  if (!state.proyectoActual) return;

  const nombreEl = querySelector<HTMLElement>('#proyecto-nombre');
  const periodoEl = querySelector<HTMLElement>('#proyecto-periodo');
  const statusEl = querySelector<HTMLElement>('#proyecto-status');

  if (nombreEl) nombreEl.textContent = state.proyectoActual.nombre;
  
  if (periodoEl) {
    periodoEl.textContent = `${MESES_ES[state.proyectoActual.mes as keyof typeof MESES_ES]} ${state.proyectoActual.anio}`;
  }
  
  if (statusEl) {
    statusEl.className = `badge ${state.proyectoActual.activo ? 'badge-active' : 'badge-inactive'}`;
    statusEl.textContent = state.proyectoActual.activo ? '✓ Activo' : '✗ Inactivo';
  }

  // Actualizar botón de finalizar/reactivar
  const finalizarBtn = querySelector<HTMLButtonElement>('#finalizar-btn');
  if (finalizarBtn) {
    if (state.proyectoActual.activo) {
      finalizarBtn.textContent = '✅ Finalizar';
      finalizarBtn.className = 'btn btn-success';
    } else {
      finalizarBtn.textContent = '♻️ Reactivar';
      finalizarBtn.className = 'btn btn-primary';
    }
  }
}

/**
 * Actualiza la card del proyecto
 */
function updateProjectCard(): void {
  if (!state.proyectoActual) return;

  const nombreEl = querySelector<HTMLElement>('#card-nombre');
  const descripcionEl = querySelector<HTMLElement>('#card-descripcion');

  if (nombreEl) nombreEl.textContent = state.proyectoActual.nombre;
  if (descripcionEl) {
    descripcionEl.textContent = state.proyectoActual.descripcion || 'Sin descripción';
  }
}

// ============================================================
// Actualización de datos
// ============================================================

/**
 * Actualiza horas de un día
 */
async function updateHoras(diaId: number, horasStr: string): Promise<void> {
  try {
    await DiaService.updateHoras(diaId, horasStr);
    await loadDias();
    updateTotalPanel();
  } catch (error) {
    console.error('Error actualizando horas:', error);
    showErrorModal('Error', 'No se pudo actualizar las horas');
  }
}

// ============================================================
// Event Listeners
// ============================================================

/**
 * Adjunta listeners a items de tareas
 */
function attachTareaListeners(): void {
  const listEl = querySelector<HTMLElement>('#tareas-list');
  if (!listEl) return;

  listEl.querySelectorAll('.tarea-item').forEach((element) => {
    // Single click: mostrar detalles
    element.addEventListener('click', (e) => {
      if ((e as PointerEvent).detail === 1) {
        const tareaId = parseInt(element.getAttribute('data-tarea-id') || '0');
        const tarea = state.tareasActuales.find((t) => t.id === tareaId);
        if (tarea) {
          const event = new CustomEvent('view-tarea', { detail: { tarea } });
          document.dispatchEvent(event);
        }
      }
    });

    // Doble click: editar
    element.addEventListener('dblclick', () => {
      const tareaId = parseInt(element.getAttribute('data-tarea-id') || '0');
      const tarea = state.tareasActuales.find((t) => t.id === tareaId);
      if (tarea) {
        const event = new CustomEvent('edit-tarea', { detail: { tarea } });
        document.dispatchEvent(event);
      }
    });
  });
}

// ============================================================
// Exports
// ============================================================

export const proyectoHandlers = {
  state,
  loadProyecto,
  loadDias,
  loadTareas,
  updateTotalPanel,
};
