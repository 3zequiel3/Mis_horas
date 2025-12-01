/**
 * Handler para gestionar las diferentes vistas del proyecto
 * Permite cambiar entre dashboard, reportes, auditoría, etc.
 * sin cambiar de página
 */

export class ProjectViewHandler {
  private currentView: string = 'dashboard';
  private proyectoId: number;
  private containers: Map<string, HTMLElement> = new Map();

  constructor(proyectoId: number) {
    this.proyectoId = proyectoId;
    this.init();
  }

  /**
   * Inicializa el handler y configura event listeners
   */
  private init(): void {
    // Obtener todos los contenedores de vistas
    this.containers.set('dashboard', document.getElementById('view-dashboard')!);
    this.containers.set('time-tracking', document.getElementById('view-time-tracking')!);
    this.containers.set('reports', document.getElementById('view-reports')!);
    this.containers.set('approvals', document.getElementById('view-approvals')!);
    this.containers.set('audit', document.getElementById('view-audit')!);
    this.containers.set('budget', document.getElementById('view-budget')!);
    this.containers.set('settings', document.getElementById('view-settings')!);

    // Escuchar evento de cambio de vista
    document.addEventListener('view-changed', (e: any) => {
      const { view } = e.detail;
      this.switchView(view);
    });
  }

  /**
   * Cambia entre vistas
   */
  private switchView(view: string): void {
    console.log(`Cambiando a vista: ${view}`);

    // Ocultar todas las vistas
    this.containers.forEach((container) => {
      if (container) {
        container.style.display = 'none';
      }
    });

    // Mostrar vista seleccionada
    const targetContainer = this.containers.get(view);
    if (targetContainer) {
      targetContainer.style.display = 'block';
      this.currentView = view;

      // Cargar datos según la vista
      this.loadViewData(view);
    }
  }

  /**
   * Carga datos específicos de cada vista
   */
  private async loadViewData(view: string): Promise<void> {
    switch (view) {
      case 'dashboard':
        // Ya está cargado por defecto
        break;

      case 'time-tracking':
        await this.loadTimeTracking();
        break;

      case 'reports':
        await this.loadReports();
        break;

      case 'approvals':
        await this.loadApprovals();
        break;

      case 'audit':
        await this.loadAudit();
        break;

      case 'budget':
        await this.loadBudget();
        break;

      case 'settings':
        // Abrir drawer de configuración
        const { ConfigDrawerHandler } = await import('./config-drawer');
        const drawer = new ConfigDrawerHandler(this.proyectoId);
        await drawer.open();
        
        // Volver a dashboard cuando se cierre
        setTimeout(() => {
          const dashboardItem = document.querySelector('.menu-item[data-view="dashboard"]');
          dashboardItem?.classList.add('active');
          this.switchView('dashboard');
        }, 100);
        break;
    }
  }

  /**
   * Carga vista de Time Tracking
   */
  private async loadTimeTracking(): Promise<void> {
    const container = this.containers.get('time-tracking');
    if (!container) return;

    container.innerHTML = `
      <div class="view-header">
        <h2>⏱️ Time Tracking</h2>
        <p>Gestión detallada de horas</p>
      </div>
      <div class="view-content">
        <div class="info-message">
          <p>📊 Vista de Time Tracking en desarrollo</p>
          <p>Aquí podrás ver gráficos de tiempo, distribución de horas, etc.</p>
        </div>
      </div>
    `;
  }

  /**
   * Carga vista de Reportes
   */
  private async loadReports(): Promise<void> {
    const container = this.containers.get('reports');
    if (!container) return;

    container.innerHTML = `
      <div class="view-header">
        <h2>📊 Reportes</h2>
        <p>Estadísticas y análisis del proyecto</p>
      </div>
      <div class="view-content">
        <div class="info-message">
          <p>📈 Vista de Reportes en desarrollo</p>
          <p>Aquí verás gráficos, métricas y estadísticas detalladas.</p>
        </div>
      </div>
    `;
  }

  /**
   * Carga vista de Aprobaciones
   */
  private async loadApprovals(): Promise<void> {
    const container = this.containers.get('approvals');
    if (!container) return;

    container.innerHTML = `
      <div class="view-header">
        <h2>✓ Aprobaciones</h2>
        <p>Aprobar horas y tareas pendientes</p>
      </div>
      <div class="view-content">
        <div class="info-message">
          <p>✅ Vista de Aprobaciones en desarrollo</p>
          <p>Aquí podrás aprobar o rechazar horas y tareas de empleados.</p>
        </div>
      </div>
    `;
  }

  /**
   * Carga vista de Auditoría
   */
  private async loadAudit(): Promise<void> {
    const container = this.containers.get('audit');
    if (!container) return;

    container.innerHTML = `
      <div class="view-header">
        <h2>📋 Auditoría</h2>
        <p>Timeline de cambios y actividad</p>
      </div>
      <div class="view-content">
        <div class="info-message">
          <p>📜 Vista de Auditoría en desarrollo</p>
          <p>Aquí verás el historial completo de cambios del proyecto.</p>
        </div>
      </div>
    `;
  }

  /**
   * Carga vista de Presupuesto
   */
  private async loadBudget(): Promise<void> {
    const container = this.containers.get('budget');
    if (!container) return;

    container.innerHTML = `
      <div class="view-header">
        <h2>💰 Presupuesto</h2>
        <p>Control de gastos y facturación</p>
      </div>
      <div class="view-content">
        <div class="info-message">
          <p>💵 Vista de Presupuesto en desarrollo</p>
          <p>Aquí gestionarás el presupuesto, addons y gastos del proyecto.</p>
        </div>
      </div>
    `;
  }

  /**
   * Retorna la vista actual
   */
  getCurrentView(): string {
    return this.currentView;
  }
}
