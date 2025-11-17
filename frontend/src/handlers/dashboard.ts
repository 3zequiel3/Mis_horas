/**
 * Handler de Dashboard - Carga de estadísticas y proyectos
 */

import { ProyectosService } from '../services/proyectos';
import { AlertUtils } from '../utils/swal';

export const DashboardHandler = {
  /**
   * Carga las estadísticas del usuario
   */
  async cargarEstadisticas() {
    try {
      const stats = await ProyectosService.getEstadisticas();

      const proyectosCountEl = document.getElementById('proyectos-count');
      const totalHoursEl = document.getElementById('total-hours');
      const weekHoursEl = document.getElementById('week-hours');
      const avgHoursEl = document.getElementById('avg-hours');

      if (proyectosCountEl) proyectosCountEl.textContent = stats.proyectos_activos.toString();
      if (totalHoursEl) totalHoursEl.textContent = stats.total_horas.toFixed(1) + 'h';
      if (weekHoursEl) weekHoursEl.textContent = stats.horas_semana.toFixed(1) + 'h';
      if (avgHoursEl) avgHoursEl.textContent = stats.promedio_diario.toFixed(1) + 'h';
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
      throw error;
    }
  },

  /**
   * Carga y renderiza los proyectos del usuario
   */
  async cargarProyectos() {
    try {
      const proyectos = await ProyectosService.getProyectos();
      const container = document.getElementById('proyectos-container')!;

      container.innerHTML = '';

      if (proyectos.length === 0) {
        container.innerHTML =
          '<p>No hay proyectos. <a href="/nuevo-proyecto">Crear uno</a></p>';
        return;
      }

      proyectos.forEach((proyecto) => {
        const item = document.createElement('div');
        item.className = 'project-item card';
        const statusClass = proyecto.activo ? 'status-active' : 'status-inactive';
        const statusText = proyecto.activo ? '✅ Activo' : '⏸️ Pausado';

        item.innerHTML = `
          <h3>${proyecto.nombre}</h3>
          <p>${proyecto.descripcion || 'Sin descripción'}</p>
          <span class="project-status ${statusClass}">${statusText}</span>
          <div class="mt-4">
            <small>${proyecto.mes}/${proyecto.anio}</small>
          </div>
        `;

        item.style.cursor = 'pointer';
        item.onclick = () => {
          localStorage.setItem('selected_proyecto', JSON.stringify(proyecto));
          window.location.href = `/proyecto/${proyecto.id}`;
        };

        container.appendChild(item);
      });
    } catch (error) {
      console.error('Error cargando proyectos:', error);
      throw error;
    }
  },

  /**
   * Carga todo el dashboard (estadísticas y proyectos)
   */
  async cargarDashboard() {
    try {
      await this.cargarEstadisticas();
      await this.cargarProyectos();
    } catch (error) {
      console.error('Error en dashboard:', error);
      const errorDiv = document.getElementById('error-message');
      if (errorDiv) {
        errorDiv.textContent = (error as Error).message;
        errorDiv.style.display = 'block';
      }
      await AlertUtils.error('Error', (error as Error).message);
    }
  },
};
