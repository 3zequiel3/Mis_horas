/**
 * Proyectos Page Handlers - Lógica separada del .astro
 */

import type { Proyecto } from '../types';
import { ProyectoService } from '../services/proyecto';
import { setHTML, setText, setVisible, querySelector, querySelectorAll } from '../utils/dom';
import Swal from 'sweetalert2';
import { MESES_ES } from '../utils/formatters';
import { formatearFechaSegura } from '../utils/date';
import { renderBadgeEstado, renderBotonesAccion } from '../utils/render';

export interface ProyectosViewState {
  proyectos: Proyecto[];
  currentView: 'table' | 'cards';
}

const state: ProyectosViewState = {
  proyectos: [],
  currentView: 'table',
};

/**
 * Carga los proyectos desde el API
 */
export async function loadProyectos(): Promise<void> {
  try {
    state.proyectos = await ProyectoService.getProyectos();

    if (state.proyectos.length === 0) {
      showEmptyState();
      return;
    }

    renderTableView();
    renderCardsView();
  } catch (error) {
    console.error('Error cargando proyectos:', error);
    showErrorState();
  }
}

/**
 * Renderiza la vista de tabla
 */
function renderTableView(): void {
  const tableBody = querySelector<HTMLTableSectionElement>('#table-body');
  if (!tableBody) return;

  tableBody.innerHTML = state.proyectos
    .map(
      (p) => {
        const url = p.tipo_proyecto === 'empleados' ? `/tablero-empleados/${p.id}` : `/proyecto/${p.id}`;
        return `
    <tr>
      <td><strong>${p.nombre}</strong></td>
      <td>${p.descripcion || '-'}</td>
      <td>${MESES_ES[p.mes as keyof typeof MESES_ES]} ${p.anio}</td>
      <td>${renderBadgeEstado(p.activo)}</td>
      <td>${formatearFechaSegura(p.fecha_creacion)}</td>
      <td>${renderBotonesAccion({
        verUrl: url,
        eliminarOnClick: `window.proyectosHandlers.deleteProyecto(${p.id})`
      })}</td>
    </tr>
  `;
      }
    )
    .join('');
}

/**
 * Renderiza la vista de tarjetas
 */
function renderCardsView(): void {
  const cardsContainer = querySelector<HTMLDivElement>('#cards-container');
  if (!cardsContainer) return;

  cardsContainer.innerHTML = state.proyectos
    .map(
      (p) => {
        const url = p.tipo_proyecto === 'empleados' ? `/tablero-empleados/${p.id}` : `/proyecto/${p.id}`;
        return `
    <div class="proyecto-card" onclick="if(window.innerWidth > 768) window.location.href='${url}'">
      <h3>${p.nombre}</h3>
      <p>${p.descripcion || 'Sin descripción'}</p>
      
      <div class="proyecto-card-info">
        <div class="proyecto-card-info-item">
          <span class="proyecto-card-info-label">Tipo</span>
          <span class="proyecto-card-info-value">${p.tipo_proyecto === 'empleados' ? '👥 Empleados' : '👤 Personal'}</span>
        </div>
        <div class="proyecto-card-info-item">
          <span class="proyecto-card-info-label">Período</span>
          <span class="proyecto-card-info-value">${MESES_ES[p.mes as keyof typeof MESES_ES]} ${p.anio}</span>
        </div>
        <div class="proyecto-card-info-item">
          <span class="proyecto-card-info-label">Estado</span>
          ${renderBadgeEstado(p.activo)}
        </div>
      </div>
      
      <div class="proyecto-card-footer">
        <div class="proyecto-card-actions">
          <a href="${url}" class="btn-sm" onclick="event.stopPropagation()">👁️ Ver</a>
          <button class="btn-sm btn-danger" onclick="event.stopPropagation(); window.proyectosHandlers.deleteProyecto(${p.id})">🗑️ Eliminar</button>
        </div>
      </div>
    </div>
  `;
      }
    )
    .join('');
}

/**
 * Inicializa los event listeners de tabs
 */
export function initializeTabs(): void {
  const tabBtns = querySelectorAll<HTMLButtonElement>('.tab-btn');

  tabBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      const tab = target.getAttribute('data-tab') as 'table' | 'cards' | null;

      if (!tab) return;

      // Actualizar estado del botón
      tabBtns.forEach((b) => b.classList.remove('active'));
      (e.target as HTMLElement).classList.add('active');

      // Cambiar vista
      const tabContents = querySelectorAll<HTMLDivElement>('.tab-content');
      tabContents.forEach((content) => {
        content.classList.remove('active');
      });

      const activeView = querySelector<HTMLDivElement>(`#${tab}-view`);
      if (activeView) {
        activeView.classList.add('active');
        state.currentView = tab;
      }
    });
  });
}

/**
 * Elimina un proyecto con confirmación
 */
export async function deleteProyecto(id: number): Promise<void> {
  const result = await Swal.fire({
    title: '¿Eliminar proyecto?',
    text: 'Esta acción no se puede deshacer',
    icon: 'warning',
    showCancelButton: true,
    background: '#0f1419',
    color: '#c8c8c8',
    confirmButtonColor: '#ef4444',
    cancelButtonColor: '#2d3746',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
    iconColor: '#f59e0b',
  });

  if (result.isConfirmed) {
    try {
      await ProyectoService.cambiarEstado(id, false);
      Swal.fire({
        title: 'Desactivado',
        text: 'Proyecto desactivado exitosamente',
        icon: 'success',
        background: '#0f1419',
        color: '#c8c8c8',
        confirmButtonColor: '#10b981',
        iconColor: '#10b981',
      });
      await loadProyectos();
    } catch (error) {
      Swal.fire({
        title: 'Error',
        text: 'No se pudo desactivar el proyecto',
        icon: 'error',
        background: '#0f1419',
        color: '#c8c8c8',
        confirmButtonColor: '#ef4444',
        iconColor: '#ef4444',
      });
    }
  }
}

/**
 * Muestra el estado vacío
 */
function showEmptyState(): void {
  setVisible('empty-message', true);
  setVisible('table-view', false);

  const viewTabs = querySelector('#view-tabs');
  if (viewTabs) {
    viewTabs.style.display = 'none';
  }
}

/**
 * Muestra el estado de error
 */
function showErrorState(): void {
  const errorMessage = querySelector('#error-message');
  if (errorMessage) {
    errorMessage.style.display = 'block';
  }
}

/**
 * Exporta los handlers como objeto global para acceso desde HTML
 */
export const proyectosHandlers = {
  deleteProyecto,
  loadProyectos,
  initializeTabs,
};
