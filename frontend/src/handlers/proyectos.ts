/**
 * Proyectos Page Handlers - Lógica separada del .astro
 */

import type { Proyecto } from '../types';
import { ProyectoService } from '../services/proyecto';
import { setHTML, setText, setVisible, querySelector, querySelectorAll } from '../utils/dom';
import Swal from 'sweetalert2';
import { MESES_ES } from '../utils/formatters';

export interface ProyectosViewState {
  proyectos: Proyecto[];
  currentView: 'table' | 'cards' | 'grid';
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
    renderGridView();
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
      (p) => `
    <tr>
      <td><strong>${p.nombre}</strong></td>
      <td>${p.descripcion || '-'}</td>
      <td>${MESES_ES[p.mes as keyof typeof MESES_ES]} ${p.anio}</td>
      <td>
        <span class="status-badge status-${p.activo ? 'active' : 'inactive'}">
          ${p.activo ? '✓ Activo' : '✗ Inactivo'}
        </span>
      </td>
      <td>${new Date(p.fecha_creacion || '').toLocaleDateString()}</td>
      <td>
        <div class="action-btns">
          <a href="/proyecto/${p.id}" class="btn-sm">👁️ Ver</a>
          <button class="btn-sm btn-danger" onclick="window.proyectosHandlers.deleteProyecto(${p.id})">🗑️ Eliminar</button>
        </div>
      </td>
    </tr>
  `
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
      (p) => `
    <div class="proyecto-card" onclick="window.location.href='/proyecto/${p.id}'">
      <h3>${p.nombre}</h3>
      <p>${p.descripcion || 'Sin descripción'}</p>
      <p><strong>${MESES_ES[p.mes as keyof typeof MESES_ES]} ${p.anio}</strong></p>
      <div class="proyecto-card-footer">
        <span class="status-badge status-${p.activo ? 'active' : 'inactive'}">
          ${p.activo ? '✓ Activo' : '✗ Inactivo'}
        </span>
        <button class="btn-sm btn-danger" onclick="event.stopPropagation(); window.proyectosHandlers.deleteProyecto(${p.id})">Eliminar</button>
      </div>
    </div>
  `
    )
    .join('');
}

/**
 * Renderiza la vista de grid
 */
function renderGridView(): void {
  const gridContainer = querySelector<HTMLDivElement>('#grid-container');
  if (!gridContainer) return;

  gridContainer.innerHTML = state.proyectos
    .map(
      (p) => `
    <div class="grid-item" onclick="window.location.href='/proyecto/${p.id}'">
      <div class="grid-item-title">${p.nombre}</div>
      <div class="grid-item-period">${MESES_ES[p.mes as keyof typeof MESES_ES]} ${p.anio}</div>
      <span class="status-badge status-${p.activo ? 'active' : 'inactive'}">
        ${p.activo ? 'Activo' : 'Inactivo'}
      </span>
    </div>
  `
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
      const tab = target.getAttribute('data-tab') as 'table' | 'cards' | 'grid' | null;

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
