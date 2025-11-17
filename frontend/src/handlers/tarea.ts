/**
 * Handlers de Tareas - Lógica separada para mejor modularidad
 */

import type { Tarea, Dia } from '../types';
import { TareaService } from '../services/tarea';
import { querySelector } from '../utils/dom';
import Swal from 'sweetalert2';

export interface TareaHandlerState {
  diasSeleccionados: Set<number>;
  diasDisponibles: Dia[];
}

const state: TareaHandlerState = {
  diasSeleccionados: new Set(),
  diasDisponibles: [],
};

/**
 * Carga los días disponibles para una nueva tarea
 */
export async function loadDiasDisponibles(
  proyectoId: number,
  anio: number,
  mes: number,
  excluirTareaId?: number
): Promise<void> {
  try {
    state.diasDisponibles = await TareaService.getDiasDisponibles(
      proyectoId,
      anio,
      mes,
      excluirTareaId
    );

    state.diasSeleccionados.clear();
    renderDiasCheckboxes();
  } catch (error) {
    console.error('Error cargando días:', error);
    showError('Error al cargar días disponibles');
  }
}

/**
 * Renderiza los checkboxes de días
 */
function renderDiasCheckboxes(): void {
  const diasContainer = querySelector<HTMLElement>('#dias-container');
  if (!diasContainer) return;

  if (state.diasDisponibles.length === 0) {
    diasContainer.innerHTML = '<p style="text-align: center; color: #999;">No hay días disponibles</p>';
    return;
  }

  diasContainer.innerHTML = state.diasDisponibles
    .map(
      (dia: Dia) => `
    <label class="dia-checkbox">
      <input 
        type="checkbox" 
        class="dia-input" 
        data-dia-id="${dia.id}"
        data-fecha="${dia.fecha}"
      />
      <span>${new Date(dia.fecha).toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        weekday: 'short',
      })}</span>
    </label>
  `
    )
    .join('');

  // Agregar event listeners a los checkboxes
  const inputs = diasContainer.querySelectorAll<HTMLInputElement>('.dia-input');
  inputs.forEach((input) => {
    input.addEventListener('change', () => {
      const diaId = parseInt(input.dataset.diaId || '0');
      if (input.checked) {
        state.diasSeleccionados.add(diaId);
      } else {
        state.diasSeleccionados.delete(diaId);
      }
    });
  });
}

/**
 * Obtiene los días seleccionados
 */
export function getDiasSeleccionados(): number[] {
  return Array.from(state.diasSeleccionados);
}

/**
 * Limpia la selección de días
 */
export function limpiarSeleccion(): void {
  state.diasSeleccionados.clear();
  const diasContainer = querySelector<HTMLElement>('#dias-container');
  if (diasContainer) {
    diasContainer.querySelectorAll<HTMLInputElement>('.dia-input').forEach((input) => {
      input.checked = false;
    });
  }
}

/**
 * Muestra un error
 */
function showError(message: string): void {
  Swal.fire({
    title: 'Error',
    text: message,
    icon: 'error',
    background: '#0f1419',
    color: '#c8c8c8',
    confirmButtonColor: '#ef4444',
    iconColor: '#ef4444',
  });
}

/**
 * Exportar handlers
 */
export const tareaHandlers = {
  state,
  loadDiasDisponibles,
  getDiasSeleccionados,
  limpiarSeleccion,
};
