/**
 * Proyecto Details Page Handlers - Lógica separada del .astro
 */

import type { Proyecto, Dia, Usuario } from '../types';
import { ProyectosService } from '../services/proyectos';
import { DiaService } from '../services/dia';
import { TareaService } from '../services/tarea';
import { AuthService } from '../services/auth';
import { querySelector, querySelectorAll } from '../utils/dom';
import { showErrorModal, showLoadingModal, closeModal } from '../utils/modals';
import { MESES_ES, horasAFormato } from '../utils/formatters';
import { formatearFechaCorta, formatearFechaSinAnio } from '../utils/date';
import {
  debeUsarHorasReales,
  obtenerHorasAMostrar,
  calcularHorasTarea as calcularHorasTareaUtil,
  calcularTotalHoras
} from '../utils/hours';
import { MultiSelectTable } from '../utils/multiselect';
import Swal from 'sweetalert2';

export interface ProyectoDetailState {
  proyectoActual: Proyecto | null;
  diasActuales: Dia[];
  tareasActuales: any[];
  usuarioActual: Usuario | null;
  mesActual: number;
  anioActual: number;
  multiSelectSemanal: MultiSelectTable | null;
  multiSelectMensual: MultiSelectTable | null;
}

const state: ProyectoDetailState = {
  proyectoActual: null,
  diasActuales: [],
  tareasActuales: [],
  usuarioActual: null,
  mesActual: new Date().getMonth() + 1,
  anioActual: new Date().getFullYear(),
  multiSelectSemanal: null,
  multiSelectMensual: null,
};

// ============================================================
// Helpers para calcular horas (usando utilidades)
// ============================================================

/**
 * Determina si debe mostrar horas reales o estimadas
 * IMPORTANTE: Usa la configuración del PROYECTO, no del usuario
 */
function useHorasReales(): boolean {
  return state.proyectoActual?.horas_reales_activas ?? false;
}

/**
 * Obtiene las horas a mostrar según configuración del usuario
 */
function getHorasAMostrar(dia: Dia): number {
  return obtenerHorasAMostrar(dia, useHorasReales());
}

/**
 * Calcula las horas de una tarea según los días asignados y configuración
 */
function calcularHorasTarea(tarea: any): string {
  return calcularHorasTareaUtil(tarea, useHorasReales());
}

/**
 * Obtiene la semana actual en formato YYYY-MM-DD
 * Solo calcula la semana si estamos viendo el mes actual
 * Para meses pasados, retorna array vacío (se mostrará mensaje especial)
 */
function getSemanActual(): string[] {
  const hoy = new Date();
  const mesActualSistema = hoy.getMonth() + 1;
  const anioActualSistema = hoy.getFullYear();
  
  const esMesActual = state.anioActual === anioActualSistema && state.mesActual === mesActualSistema;
  

  // Si no es el mes actual, retornar array vacío
  if (!esMesActual) {
    return [];
  }

  // Calcular semana actual solo para el mes en curso
  const diaActual = hoy.getDay(); // 0 = Domingo, 1 = Lunes, ..., 6 = Sábado
  const diaInicioSemana = state.usuarioActual?.dia_inicio_semana || 0; // 0 = Domingo, 1 = Lunes

  let diasAtras = diaActual - diaInicioSemana;
  if (diasAtras < 0) {
    diasAtras += 7;
  }

  const primDia = hoy.getDate() - diasAtras;
  const semana = [];

  for (let i = primDia; i <= primDia + 6; i++) {
    const fecha = new Date(hoy.getFullYear(), hoy.getMonth(), i);
    const year = fecha.getFullYear();
    const month = String(fecha.getMonth() + 1).padStart(2, '0');
    const day = String(fecha.getDate()).padStart(2, '0');
    const fechaStr = `${year}-${month}-${day}`;
    semana.push(fechaStr);
  }

  console.log('📅 [SEMANA] Días de la semana actual:', semana);

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

    state.proyectoActual = await ProyectosService.getProyecto(proyectoId);

    if (!state.proyectoActual) {
      window.location.href = '/proyectos';
      return;
    }

    // Actualizar UI
    updateProjectHeader();
    updateProjectCard();

    // Verificar si es proyecto con empleados y redirigir a la vista correcta
    if (state.proyectoActual.tipo_proyecto === 'empleados') {
      window.location.href = `/tablero-empleados/${proyectoId}`;
      return;
    }

    // Establecer mes y año
    state.mesActual = state.proyectoActual.mes;
    state.anioActual = state.proyectoActual.anio;

    // Verificar si el mes actual del proyecto no coincide con el mes real
    // y crear automáticamente el mes siguiente si es necesario
    await verificarYCrearMesSiguiente();

    // Cargar datos para proyecto personal
    await loadDias();
    await loadTareas();
    updateTotalPanel();
  } catch (error) {
    console.error('Error cargando proyecto:', error);
    showErrorModal('Error', 'No se pudo cargar el proyecto');
  }
}

/**
 * Carga proyecto con empleados - muestra tabla por cada empleado
 */
async function loadProyectoConEmpleados(): Promise<void> {
  try {
    if (!state.proyectoActual || !state.proyectoActual.empleados) return;

    const { EmpleadosService } = await import('../services/empleados');
    const empleados = await EmpleadosService.getEmpleadosByProyecto(state.proyectoActual.id);

    const diasColumn = document.querySelector('.dias-column');
    if (!diasColumn) return;

    // Limpiar contenido
    diasColumn.innerHTML = '';

    // Crear sección por cada empleado
    for (let i = 0; i < empleados.length; i++) {
      const empleado = empleados[i];
      const isFirst = i === 0; // El primero estará abierto por defecto

      const diasEmpleado = await DiaService.getDiasMes(
        state.proyectoActual.id,
        state.anioActual,
        state.mesActual,
        empleado.id
      );

      // Obtener semana actual
      const semanaFechas = getSemanActual();
      const diasSemana = diasEmpleado.filter((dia) => {
        const diaFecha = new Date(dia.fecha).toISOString().split('T')[0];
        return semanaFechas.includes(diaFecha);
      });

      // Calcular totales
      const totalTrabajadas = diasSemana.reduce((sum, dia) => sum + (dia.horas_trabajadas || 0), 0);
      const totalReales = diasSemana.reduce((sum, dia) => sum + (dia.horas_reales || 0), 0);

      // Crear HTML para el empleado con acordeón
      const seccionHTML = `
        <div class="section empleado-section" data-empleado-id="${empleado.id}">
          <div class="empleado-accordion-header ${isFirst ? 'active' : ''}" data-empleado-accordion="${empleado.id}">
            <h2>${empleado.nombre}</h2>
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
                      ${state.proyectoActual.horas_reales_activas ? '<th>Horas Reales</th>' : ''}
                    </tr>
                  </thead>
                  <tbody id="dias-tbody-${empleado.id}">
                    ${renderDiasEmpleado(diasSemana, state.proyectoActual.horas_reales_activas)}
                  </tbody>
                  <tfoot>
                    <tr class="totals-row">
                      <td><strong>Total:</strong></td>
                      <td></td>
                      <td><strong>${horasAFormato(totalTrabajadas)}</strong></td>
                      ${state.proyectoActual.horas_reales_activas ? `<td><strong>${horasAFormato(totalReales)}</strong></td>` : ''}
                    </tr>
                  </tfoot>
                </table>
              </div>

              <div class="empleado-actions">
                <button class="btn btn-danger btn-export-empleado" data-empleado-id="${empleado.id}" data-empleado-nombre="${empleado.nombre}">
                  📥 Exportar PDF - ${empleado.nombre}
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
          exportarPDFEmpleado(parseInt(empleadoId), empleadoNombre);
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
            await loadProyectoConEmpleados();
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
}

/**
 * Renderiza los días de un empleado
 */
function renderDiasEmpleado(dias: Dia[], mostrarHorasReales: boolean): string {
  if (!dias.length) {
    return `<tr><td colspan="${mostrarHorasReales ? 4 : 3}" class="text-center">No hay días para mostrar</td></tr>`;
  }

  return dias.map(dia => {
    const horasTrabajadas = horasAFormato(dia.horas_trabajadas || 0);
    const horasReales = horasAFormato(dia.horas_reales || 0);

    return `
      <tr data-dia-id="${dia.id}">
        <td>${formatearFechaSinAnio(dia.fecha)}</td>
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
}

/**
 * Exporta PDF de un empleado específico
 */
async function exportarPDFEmpleado(empleadoId: number, empleadoNombre: string): Promise<void> {
  try {
    const { AlertUtils } = await import('../utils/swal');
    AlertUtils.loading('Generando PDF...');

    // Obtener todos los días del empleado del mes
    const dias = await DiaService.getDiasMes(
      state.proyectoActual!.id,
      state.anioActual,
      state.mesActual,
      empleadoId
    );

    // Obtener tareas (filtrar por días del empleado)
    const todasTareas = await TareaService.getTareasProyecto(state.proyectoActual!.id);
    const tareasEmpleado = todasTareas.filter(tarea =>
      tarea.dias && tarea.dias.some((dia: Dia) => dia.empleado_id === empleadoId)
    );

    const { generatePDFFromTemplate } = await import('../utils/pdf');
    const mes = MESES_ES[state.mesActual as keyof typeof MESES_ES] || `Mes ${state.mesActual}`;

    await generatePDFFromTemplate(
      `${state.proyectoActual!.nombre} - ${empleadoNombre}`,
      mes,
      state.anioActual,
      tareasEmpleado,
      dias
    );

    AlertUtils.close();
    await AlertUtils.success('Éxito', 'PDF descargado correctamente');
  } catch (error) {
    console.error('Error generando PDF:', error);
    const { AlertUtils } = await import('../utils/swal');
    AlertUtils.close();
    await AlertUtils.error('Error', 'No se pudo generar el PDF');
  }
}

/**
 * Verifica y crea automáticamente el mes siguiente si estamos en un mes nuevo
 */
async function verificarYCrearMesSiguiente(): Promise<void> {
  if (!state.proyectoActual) return;

  const hoy = new Date();
  const mesRealActual = hoy.getMonth() + 1; // 1-12
  const anioRealActual = hoy.getFullYear();

  // Si el mes actual del sistema es diferente al mes del proyecto
  if (anioRealActual > state.anioActual || 
      (anioRealActual === state.anioActual && mesRealActual > state.mesActual)) {
    
    console.log(`[AUTO-MES] Detectado cambio de mes. Sistema: ${mesRealActual}/${anioRealActual}, Proyecto: ${state.mesActual}/${state.anioActual}`);
    
    // Importar el handler de meses
    const { MesesHandler } = await import('./meses');
    
    // Cargar meses disponibles
    await MesesHandler.loadMeses(state.proyectoActual.id);
    
    // Verificar si el mes actual del sistema ya existe
    if (!MesesHandler.mesYaExiste(anioRealActual, mesRealActual)) {
      console.log(`[AUTO-MES] Creando automáticamente mes ${mesRealActual}/${anioRealActual}`);
      
      try {
        const mesCreado = await MesesHandler.crearMesAutomatico(
          state.proyectoActual.id,
          anioRealActual,
          mesRealActual
        );
        
        if (mesCreado) {
          console.log(`[AUTO-MES] Mes ${mesRealActual}/${anioRealActual} creado exitosamente`);
          
          // Actualizar el estado para usar el nuevo mes
          state.mesActual = mesRealActual;
          state.anioActual = anioRealActual;
          state.proyectoActual.mes = mesRealActual;
          state.proyectoActual.anio = anioRealActual;
        }
      } catch (error) {
        console.error('[AUTO-MES] Error creando mes automático:', error);
      }
    } else {
      console.log(`[AUTO-MES] El mes ${mesRealActual}/${anioRealActual} ya existe`);
      
      // Solo actualizar al mes actual si ya existe
      state.mesActual = mesRealActual;
      state.anioActual = anioRealActual;
      state.proyectoActual.mes = mesRealActual;
      state.proyectoActual.anio = anioRealActual;
    }
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

    if (mesStatus === 'futuro') {
      // Solo bloquear meses futuros (no se pueden editar)
      const html = `
        <tr>
          <td colspan="4" class="mes-message-row">
            <div class="mes-message">
              <span class="mes-icon">📅</span>
              <span class="mes-text">Mes aún no iniciado</span>
            </div>
          </td>
        </tr>
      `;

      if (diasTbody) diasTbody.innerHTML = html;
      if (mesDiasTbody) mesDiasTbody.innerHTML = html;

      // Ocultar totales cuando el mes es futuro
      toggleTotalsRow(false);
      return;
    }

    // Mostrar totales para meses actuales y pasados
    toggleTotalsRow(true);

    // Cargar días del mes (una sola llamada al backend)
    state.diasActuales = await DiaService.getDiasMes(
      state.proyectoActual.id,
      state.anioActual,
      state.mesActual
    );

    // Si no hay días, mostrar mensaje informativo
    if (state.diasActuales.length === 0) {
      const html = `
        <tr>
          <td colspan="4" class="mes-message-row">
            <div class="mes-message">
              <span class="mes-icon">📭</span>
              <span class="mes-text">No hay días registrados para este mes</span>
            </div>
          </td>
        </tr>
      `;

      if (diasTbody) diasTbody.innerHTML = html;
      if (mesDiasTbody) mesDiasTbody.innerHTML = html;
      toggleTotalsRow(false);
      return;
    }

    // Obtener días de la semana actual (filtrado en memoria, más rápido)
    const semanaFechas = getSemanActual();
    
    // Si semanaFechas está vacío, es porque estamos viendo un mes pasado
    if (semanaFechas.length === 0) {
      // Mostrar mensaje bonito de mes terminado
      const hoy = new Date();
      const mesActualSistema = hoy.getMonth() + 1;
      const anioActualSistema = hoy.getFullYear();
      const esMesFuturo = state.anioActual > anioActualSistema || 
                          (state.anioActual === anioActualSistema && state.mesActual > mesActualSistema);
      
      const html = `
        <tr>
          <td colspan="4" class="mes-message-row">
            <div class="mes-message mes-terminado">
              <span class="mes-icon">📅</span>
              <span class="mes-text">${esMesFuturo ? 'Mes Futuro' : 'Mes Finalizado'}</span>
              <p style="margin-top: 8px; font-size: 0.9em; opacity: 0.8;">
                ${esMesFuturo 
                  ? 'Este mes aún no ha comenzado' 
                  : 'Has llegado al final de este mes. ¡Buen trabajo!'}
              </p>
            </div>
          </td>
        </tr>
      `;
      if (diasTbody) diasTbody.innerHTML = html;
      toggleTotalsRow(false);
    } else {
      // Filtrar días de la semana actual
      const diasSemana = state.diasActuales.filter((dia) => {
        const diaFecha = new Date(dia.fecha).toISOString().split('T')[0];
        return semanaFechas.includes(diaFecha);
      });
      
      // Renderizar tabla normal para el mes actual
      renderTablaDias(diasSemana, 'dias-tbody', 'total-trabajadas', 'total-reales');
      toggleTotalsRow(true);
    }

    // Renderizar tabla mensual completa (siempre disponible)
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

    state.tareasActuales = await TareaService.getTareasProyecto(
      state.proyectoActual.id,
      state.mesActual,
      state.anioActual
    );

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

  // Usar DocumentFragment para mejor rendimiento
  const fragment = document.createDocumentFragment();
  const usarHorasReales = useHorasReales();
  
  let totalTrabajadas = 0;
  let totalReales = 0;

  // Optimización: crear todas las filas antes de agregarlas al DOM
  dias.forEach((dia) => {
    totalTrabajadas += dia.horas_trabajadas || 0;
    totalReales += dia.horas_reales || 0;

    const row = document.createElement('tr');
    row.setAttribute('data-dia-id', dia.id.toString());
    row.className = (dia.horas_trabajadas || 0) === 0 ? 'dia-sin-horas' : 'dia-con-horas';

    // Construir HTML de forma más eficiente
    const columnasExtras = usarHorasReales
      ? `<td title="Horas Reales"><strong>${horasAFormato(dia.horas_reales || 0)}</strong></td>`
      : '<td style="display: none;"></td>';

    row.innerHTML = `
      <td>${formatearFechaCorta(dia.fecha)}</td>
      <td>${dia.dia_semana}</td>
      <td>
        <input type="text" class="horas-input horas-trabajadas" 
          data-dia-id="${dia.id}" 
          value="${horasAFormato(dia.horas_trabajadas || 0)}" 
          autocomplete="off" />
      </td>
      ${columnasExtras}
    `;

    // Event listener para cambios (delegación de eventos más eficiente)
    const input = row.querySelector<HTMLInputElement>('.horas-trabajadas');
    if (input) {
      input.addEventListener('change', () => updateHoras(dia.id, input.value));
      // También actualizar al presionar Enter
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          input.blur();
        }
      });
    }

    fragment.appendChild(row);
  });

  // Una sola operación de DOM para agregar todas las filas
  tbody.innerHTML = '';
  tbody.appendChild(fragment);

  // Actualizar visibilidad de columnas
  updateColumnVisibility();

  // Actualizar totales
  updateTotals(totalTrabId, totalRealId, totalTrabajadas, totalReales);

  // Refrescar multi-select si está activo
  if (tbodyId === 'dias-tbody' && state.multiSelectSemanal) {
    state.multiSelectSemanal.refresh();
  } else if (tbodyId === 'mes-dias-tbody' && state.multiSelectMensual) {
    state.multiSelectMensual.refresh();
  }
}

/**
 * Actualiza la visibilidad de columnas de horas reales
 */
/**
 * Actualiza una fila de día en una tabla específica sin re-renderizar toda la tabla
 */
function updateDiaRowInTable(dia: Dia, tbodyId: string): void {
  const tbody = document.querySelector<HTMLTableSectionElement>(`#${tbodyId}`);
  if (!tbody) return;
  
  // Buscar la fila del día
  const row = tbody.querySelector<HTMLTableRowElement>(`tr[data-dia-id="${dia.id}"]`);
  if (!row) return;
  
  // Actualizar clases según las horas trabajadas
  row.className = (dia.horas_trabajadas || 0) === 0 ? 'dia-sin-horas' : 'dia-con-horas';
  
  // Actualizar el input de horas trabajadas
  const input = row.querySelector<HTMLInputElement>('.horas-trabajadas');
  if (input) {
    input.value = horasAFormato(dia.horas_trabajadas || 0);
  }
  
  // Actualizar horas reales si la columna está visible
  const usarHorasReales = useHorasReales();
  if (usarHorasReales) {
    const horasRealesCell = row.cells[3]; // 4ta columna (índice 3)
    if (horasRealesCell) {
      horasRealesCell.innerHTML = `<strong>${horasAFormato(dia.horas_reales || 0)}</strong>`;
    }
  }
}

/**
 * Actualiza los totales desde el estado actual sin recargar
 */
function updateTotalsFromState(): void {
  // Obtener días de la semana actual
  const semanaFechas = getSemanActual();
  const diasSemana = state.diasActuales.filter((dia) => {
    const diaFecha = new Date(dia.fecha).toISOString().split('T')[0];
    return semanaFechas.includes(diaFecha);
  });
  
  // Calcular totales semanales
  const totalSemanaTrabajadas = diasSemana.reduce((sum, d) => sum + (d.horas_trabajadas || 0), 0);
  const totalSemanaReales = diasSemana.reduce((sum, d) => sum + (d.horas_reales || 0), 0);
  
  // Calcular totales mensuales
  const totalMesTrabajadas = state.diasActuales.reduce((sum, d) => sum + (d.horas_trabajadas || 0), 0);
  const totalMesReales = state.diasActuales.reduce((sum, d) => sum + (d.horas_reales || 0), 0);
  
  // Actualizar UI
  updateTotals('total-trabajadas', 'total-reales', totalSemanaTrabajadas, totalSemanaReales);
  updateTotals('mes-total-trabajadas', 'mes-total-reales', totalMesTrabajadas, totalMesReales);
  updateTotalPanel();
}

function updateColumnVisibility(): void {
  const usarHorasReales = useHorasReales();
  
  // Headers - Tabla semanal
  const thRealHeader = querySelector<HTMLElement>('#th-horas-reales');
  if (thRealHeader) {
    thRealHeader.style.display = usarHorasReales ? '' : 'none';
  }
  
  // Footer - Tabla semanal
  const tdTotalRealFooter = querySelector<HTMLElement>('#td-total-reales');
  if (tdTotalRealFooter) {
    tdTotalRealFooter.style.display = usarHorasReales ? '' : 'none';
  }
  
  // Headers - Modal de mes completo
  const thMesRealHeader = querySelector<HTMLElement>('#th-mes-horas-reales');
  if (thMesRealHeader) {
    thMesRealHeader.style.display = usarHorasReales ? '' : 'none';
  }
  
  // Footer - Modal de mes completo  
  const tdMesTotalRealFooter = querySelector<HTMLElement>('#td-mes-total-reales');
  if (tdMesTotalRealFooter) {
    tdMesTotalRealFooter.style.display = usarHorasReales ? '' : 'none';
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
    const hoy = new Date();
    const mesActualReal = hoy.getMonth() + 1;
    const anioActualReal = hoy.getFullYear();
    const esMesPasado = state.proyectoActual.anio < anioActualReal || 
                        (state.proyectoActual.anio === anioActualReal && state.proyectoActual.mes < mesActualReal);
    
    if (esMesPasado) {
      periodoEl.innerHTML = `${MESES_ES[state.proyectoActual.mes as keyof typeof MESES_ES]} ${state.proyectoActual.anio} <span style="margin-left: 8px; padding: 2px 8px; background: #555; border-radius: 4px; font-size: 0.75rem;">✓ Terminado</span>`;
    } else {
      periodoEl.textContent = `${MESES_ES[state.proyectoActual.mes as keyof typeof MESES_ES]} ${state.proyectoActual.anio}`;
    }
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
    // Actualizar en el backend
    const diaActualizado = await DiaService.updateHoras(diaId, horasStr);
    
    if (!diaActualizado) {
      showErrorModal('Error', 'No se pudo actualizar las horas');
      return;
    }
    
    // Actualizar el día en el estado local
    const index = state.diasActuales.findIndex(d => d.id === diaId);
    if (index !== -1) {
      state.diasActuales[index] = diaActualizado;
    }
    
    // Actualizar la fila visualmente en ambas tablas (semanal y mensual)
    updateDiaRowInTable(diaActualizado, 'dias-tbody');
    updateDiaRowInTable(diaActualizado, 'mes-dias-tbody');
    
    // Actualizar solo los totales en lugar de recargar todo
    updateTotalsFromState();
    
    // Recargar tareas en background sin bloquear (solo si hay tareas que afectar)
    if (state.tareasActuales.length > 0) {
      loadTareas().catch(err => console.error('Error recargando tareas:', err));
    }
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
// Multi-Select Management
// ============================================================

/**
 * Crea los controles de selección en el header
 */
function createSelectionHeaderControls(sectionId: string): HTMLElement {
  const controls = document.createElement('div');
  controls.className = 'selection-header-controls';
  controls.id = `${sectionId}-selection-controls`;

  controls.innerHTML = `
    <div class="selection-info">
      <span class="selection-count" id="${sectionId}-selection-count">0 días seleccionados</span>
    </div>
    <div class="selection-actions">
      <button class="selection-btn selection-btn-create" id="${sectionId}-btn-create-task">
        ✅ Crear tarea
      </button>
      <button class="selection-btn selection-btn-cancel" id="${sectionId}-btn-cancel">
        ✖ Cancelar
      </button>
    </div>
  `;

  return controls;
}

/**
 * Muestra u oculta los controles de selección en el header
 */
function toggleSelectionControls(sectionId: string, isActive: boolean): void {
  const controls = querySelector<HTMLElement>(`#${sectionId}-selection-controls`);
  const title = querySelector<HTMLElement>(`#${sectionId}-title`);

  if (controls) {
    if (isActive) {
      controls.classList.add('active');
      if (sectionId === 'mes-section') {
        // Para el modal, solo mostrar el contenedor
        controls.style.display = 'flex';
      } else {
        // Para la sección semanal, ocultar título
        if (title) {
          title.style.display = 'none';
        }
      }
    } else {
      controls.classList.remove('active');
      if (sectionId === 'mes-section') {
        // Para el modal, ocultar el contenedor
        controls.style.display = 'none';
      } else {
        // Para la sección semanal, restaurar título
        if (title) {
          title.style.display = '';
        }
      }
    }
  }
}

/**
 * Actualiza el contador de días seleccionados
 */
function updateSelectionCount(sectionId: string, selectedIds: Set<number>): void {
  const countEl = querySelector<HTMLElement>(`#${sectionId}-selection-count`);
  if (countEl) {
    const count = selectedIds.size;
    countEl.textContent = `${count} día${count !== 1 ? 's' : ''} seleccionado${count !== 1 ? 's' : ''}`;
  }

  const btnCreateTask = querySelector<HTMLButtonElement>(`#${sectionId}-btn-create-task`);
  if (btnCreateTask) {
    btnCreateTask.disabled = selectedIds.size === 0;
  }
}

/**
 * Inicializa el modo de selección múltiple para una tabla
 */
function initMultiSelectForTable(
  tableId: string,
  sectionId: string,
  multiSelectInstance: MultiSelectTable | null
): MultiSelectTable {
  // Callback cuando cambia el modo de selección
  const onModeChange = (isActive: boolean) => {
    toggleSelectionControls(sectionId, isActive);
  };

  // Callback cuando cambia la selección
  const onSelectionChange = (selectedIds: Set<number>) => {
    updateSelectionCount(sectionId, selectedIds);
  };

  // Crear instancia de multi-select
  const instance = new MultiSelectTable({
    tableSelector: `#${tableId}`,
    rowSelector: 'tbody tr:not(.loading-row)',
    holdDuration: 1500,
    onModeChange,
    onSelectionChange
  });

  // Event listener para botón de crear tarea
  const btnCreateTask = querySelector<HTMLButtonElement>(`#${sectionId}-btn-create-task`);
  if (btnCreateTask) {
    btnCreateTask.addEventListener('click', () => {
      const selectedIds = instance.getSelectedIds();

      // Disparar evento para abrir modal de crear tarea con días pre-seleccionados
      const event = new CustomEvent('create-tarea-with-dias', {
        detail: { diaIds: selectedIds }
      });
      document.dispatchEvent(event);

      // Salir del modo selección
      instance.exitSelectionMode();
    });
  }

  // Event listener para botón de cancelar
  const btnCancel = querySelector<HTMLButtonElement>(`#${sectionId}-btn-cancel`);
  if (btnCancel) {
    btnCancel.addEventListener('click', () => {
      instance.exitSelectionMode();
    });
  }

  return instance;
}

/**
 * Inicializa el modo de selección múltiple para las tablas
 */
export function initMultiSelect(): void {
  // Agregar controles a la sección de "Esta Semana" (solo para proyectos personales, no empleados)
  const diasSection = querySelector<HTMLElement>('.dias-column .section:not(.empleado-section)');
  if (diasSection) {
    // Buscar el h2 y convertir su contenedor en section-header
    const h2 = diasSection.querySelector('h2');
    if (h2) {
      // Crear wrapper para el header
      const headerWrapper = document.createElement('div');
      headerWrapper.className = 'section-header';

      // Agregar ID al título
      h2.id = 'semana-section-title';

      // Crear controles
      const controls = createSelectionHeaderControls('semana-section');

      // Insertar antes del h2 actual
      h2.parentNode!.insertBefore(headerWrapper, h2);
      headerWrapper.appendChild(h2);
      headerWrapper.appendChild(controls);

      // Inicializar multi-select para tabla semanal
      state.multiSelectSemanal = initMultiSelectForTable('dias-table', 'semana-section', state.multiSelectSemanal);
    }
  }

  // Inicializar multi-select para tabla mensual (modal)
  // Los controles ya están en el HTML del modal
  state.multiSelectMensual = initMultiSelectForTable('mes-dias-table', 'mes-section', state.multiSelectMensual);
}

/**
 * Limpia el multi-select al destruir la página
 */
export function cleanupMultiSelect(): void {
  if (state.multiSelectSemanal) {
    state.multiSelectSemanal.destroy();
    state.multiSelectSemanal = null;
  }
  if (state.multiSelectMensual) {
    state.multiSelectMensual.destroy();
    state.multiSelectMensual = null;
  }
}

// ============================================================
// Exports
// ============================================================

async function mostrarModalConfiguracion(): Promise<void> {
  const proyecto = state.proyectoActual;
  if (!proyecto) return;

  const { value: formValues } = await Swal.fire({
    title: 'Configuración del Proyecto',
    html: `
      <div style="text-align: left; padding: 15px; max-width: 400px; margin: 0 auto;">
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
          <p style="color: #9ca3af; font-size: 13px; margin-top: 8px; margin-left: 28px;">
            Muestra una columna adicional para registrar las horas reales trabajadas.
          </p>
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
    width: '450px',
    preConfirm: () => {
      const horasRealesCheckbox = document.getElementById('horas-reales-checkbox') as HTMLInputElement;
      return {
        horas_reales_activas: horasRealesCheckbox.checked
      };
    }
  });

  if (formValues && state.proyectoActual) {
    try {
      await ProyectosService.updateConfiguracion(
        state.proyectoActual.id,
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
}

export const proyectoHandlers = {
  state,
  loadProyecto,
  loadDias,
  loadTareas,
  updateTotalPanel,
  initMultiSelect,
  cleanupMultiSelect,
  mostrarModalConfiguracion,
};
