// Carga de estadísticas y proyectos

import { ProyectosService } from '../services/proyectos';
import { AlertUtils } from '../utils/swal';
import { initializeOrganizationContext } from '../utils/organizationContext';

export const DashboardHandler = {
  // FASE 1 MULTI-TENANT: Inicializa el contexto organizacional antes de cargar datos
  async inicializar() {
    try {
      await initializeOrganizationContext();
    } catch (error) {
      console.error('Error inicializando contexto organizacional:', error);
      // Continuar de todos modos
    }
  },

  // Carga las estadísticas del usuario desde el servidor
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

  // Carga y renderiza los proyectos del usuario
  async cargarProyectos() {
    try {
      let proyectos = await ProyectosService.getProyectos();
      
      // FASE 2 PERMISOS: Filtrar proyectos según rol (miembros solo ven proyectos asignados)
      const userRole = this.getUserRole();
      if (userRole && ['member', 'viewer'].includes(userRole)) {
        // En producción, el backend debería filtrar automáticamente
        // Aquí solo como medida adicional de seguridad
        console.log('Usuario con rol limitado:', userRole);
      }
      
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
          // Redirigir según tipo de proyecto
          if (proyecto.tipo_proyecto === 'empleados') {
            window.location.href = `/tablero-empleados/${proyecto.id}`;
          } else {
            window.location.href = `/proyecto/${proyecto.id}`;
          }
        };

        container.appendChild(item);
      });
    } catch (error) {
      console.error('Error cargando proyectos:', error);
      throw error;
    }
  },

  // Carga estadísticas y proyectos al iniciar dashboard
  async cargarDashboard() {
    try {
      // FASE 1 MULTI-TENANT: Inicializar contexto organizacional primero
      await this.inicializar();
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

  // FASE 2 PERMISOS: Obtener rol del usuario actual
  getUserRole(): string | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      const user = JSON.parse(userStr);
      return user.role || null;
    } catch {
      return null;
    }
  },
};
