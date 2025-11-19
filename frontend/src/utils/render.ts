/**
 * Utilidades para renderizado de componentes HTML
 */

import type { Dia } from '../types';
import { horasAFormato } from './formatters';
import { formatearFechaSinAnio } from './date';

/**
 * Renderiza una fila de tabla para un día de empleado
 */
export function renderFilaDiaEmpleado(
  dia: Dia,
  mostrarHorasReales: boolean,
  incluirInputs: boolean = true
): string {
  const horasTrabajadas = horasAFormato(dia.horas_trabajadas || 0);
  const horasReales = horasAFormato(dia.horas_reales || 0);

  const columnaHoras = incluirInputs
    ? `<input 
        type="text" 
        class="horas-input" 
        value="${horasTrabajadas}" 
        data-dia-id="${dia.id}"
        placeholder="00:00"
      />`
    : `<strong>${horasTrabajadas}</strong>`;

  return `
    <tr data-dia-id="${dia.id}">
      <td>${formatearFechaSinAnio(dia.fecha)}</td>
      <td>${dia.dia_semana}</td>
      <td>${columnaHoras}</td>
      ${mostrarHorasReales ? `<td>${horasReales}</td>` : ''}
    </tr>
  `;
}

/**
 * Renderiza múltiples filas de días para un empleado
 */
export function renderFilasDiasEmpleado(
  dias: Dia[],
  mostrarHorasReales: boolean,
  incluirInputs: boolean = true
): string {
  if (!dias.length) {
    const colspan = mostrarHorasReales ? 4 : 3;
    return `<tr><td colspan="${colspan}" class="text-center">No hay días para mostrar</td></tr>`;
  }

  return dias
    .map(dia => renderFilaDiaEmpleado(dia, mostrarHorasReales, incluirInputs))
    .join('');
}

/**
 * Renderiza un badge de estado
 */
export function renderBadgeEstado(activo: boolean): string {
  const statusClass = activo ? 'status-active' : 'status-inactive';
  const statusText = activo ? '✓ Activo' : '✗ Inactivo';
  
  return `<span class="status-badge ${statusClass}">${statusText}</span>`;
}

/**
 * Renderiza un elemento vacío con mensaje
 */
export function renderEstadoVacio(mensaje: string, colspan: number = 4): string {
  return `
    <tr>
      <td colspan="${colspan}" class="text-center">
        <p style="color: var(--text-secondary); padding: 1rem;">
          ${mensaje}
        </p>
      </td>
    </tr>
  `;
}

/**
 * Renderiza botones de acción comunes
 */
export function renderBotonesAccion(config: {
  verUrl?: string;
  editarOnClick?: string;
  eliminarOnClick?: string;
  customButtons?: string;
}): string {
  const buttons: string[] = [];
  
  if (config.verUrl) {
    buttons.push(`<a href="${config.verUrl}" class="btn-sm">👁️ Ver</a>`);
  }
  
  if (config.editarOnClick) {
    buttons.push(`<button class="btn-sm btn-primary" onclick="${config.editarOnClick}">✏️ Editar</button>`);
  }
  
  if (config.eliminarOnClick) {
    buttons.push(`<button class="btn-sm btn-danger" onclick="${config.eliminarOnClick}">🗑️ Eliminar</button>`);
  }
  
  if (config.customButtons) {
    buttons.push(config.customButtons);
  }
  
  return `<div class="action-btns">${buttons.join('')}</div>`;
}
