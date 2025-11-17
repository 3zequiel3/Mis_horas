/**
 * Utility para gestionar la selección múltiple de días en tablas
 */

import { AlertUtils } from './swal';

export interface MultiselectOptions {
  tableSelector: string;
  rowSelector: string;
  holdDuration?: number;
  onSelectionChange?: (selectedIds: Set<number>) => void;
  onModeChange?: (isActive: boolean) => void;
}

export class MultiSelectTable {
  private table: HTMLElement | null;
  private selectedRows: Set<number> = new Set();
  private isSelectionMode: boolean = false;
  private holdTimer: NodeJS.Timeout | null = null;
  private options: MultiselectOptions;
  private readonly HOLD_DURATION: number;

  constructor(options: MultiselectOptions) {
    this.options = options;
    this.HOLD_DURATION = options.holdDuration || 1500; // 1.5 segundos por defecto
    this.table = document.querySelector(options.tableSelector);
    this.init();
  }

  private init(): void {
    if (!this.table) {
      console.warn('MultiSelect: Table not found');
      return;
    }

    this.attachEventListeners();
  }

  private attachEventListeners(): void {
    if (!this.table) return;

    const rows = this.table.querySelectorAll(this.options.rowSelector);

    rows.forEach((row) => {
      const element = row as HTMLElement;
      
      // Doble click para PC - activar modo selección
      element.addEventListener('dblclick', (e) => this.handleDoubleClick(e, element));
      
      // Touch events para móvil - mantener pulsado
      element.addEventListener('touchstart', (e) => this.handleTouchStart(e, element), { passive: false });
      element.addEventListener('touchend', () => this.handleTouchEnd());
      element.addEventListener('touchcancel', () => this.handleTouchEnd());
      
      // Click simple para selección cuando el modo está activo
      element.addEventListener('click', (e) => this.handleClick(e, element));
    });
  }

  private async handleDoubleClick(event: MouseEvent, element: HTMLElement): Promise<void> {
    // Evitar activar si se hace doble click en un input
    if ((event.target as HTMLElement).tagName === 'INPUT') {
      return;
    }
    
    event.preventDefault();
    
    const diaId = this.getDiaIdFromRow(element);
    if (diaId !== null) {
      if (!this.isSelectionMode) {
        // Activar modo selección con el primer elemento
        await this.activateSelectionMode(diaId, element);
      } else {
        // Si ya está en modo selección, toggle este elemento
        await this.toggleRowSelection(diaId, element);
      }
    }
  }

  private handleTouchStart(e: TouchEvent, element: HTMLElement): void {
    if (this.isSelectionMode) return;
    
    // Prevenir comportamiento por defecto solo si no estamos en un input
    const target = e.target as HTMLElement;
    if (!target.closest('input, button, a')) {
      e.preventDefault();
    }
    
    this.startHoldTimer(element);
  }

  private handleTouchEnd(): void {
    this.cancelHoldTimer();
  }

  private async handleClick(e: Event, element: HTMLElement): Promise<void> {
    // Solo actuar si estamos en modo selección
    if (!this.isSelectionMode) return;
    
    // Prevenir navegación o acciones por defecto
    e.preventDefault();
    e.stopPropagation();
    
    const diaId = this.getDiaIdFromRow(element);
    if (diaId !== null) {
      await this.toggleRowSelection(diaId, element);
    }
  }

  private startHoldTimer(element: HTMLElement): void {
    this.holdTimer = setTimeout(async () => {
      const diaId = this.getDiaIdFromRow(element);
      if (diaId !== null) {
        await this.activateSelectionMode(diaId, element);
      }
    }, this.HOLD_DURATION);
  }

  private cancelHoldTimer(): void {
    if (this.holdTimer) {
      clearTimeout(this.holdTimer);
      this.holdTimer = null;
    }
  }

  private getDiaIdFromRow(row: HTMLElement): number | null {
    // Buscar el input de horas para obtener el dia-id
    const input = row.querySelector('[data-dia-id]') as HTMLElement;
    if (input) {
      const diaId = input.getAttribute('data-dia-id');
      return diaId ? parseInt(diaId) : null;
    }
    return null;
  }

  /**
   * Verifica si un día tiene horas > 0
   */
  private async verificarDiaTieneHoras(row: HTMLElement): Promise<boolean> {
    // Verificar por clase
    if (row.classList.contains('dia-sin-horas')) {
      return false;
    }
    if (row.classList.contains('dia-con-horas')) {
      return true;
    }
    
    // Fallback: leer el input de horas
    const input = row.querySelector<HTMLInputElement>('.horas-input');
    if (input) {
      const valor = input.value.trim();
      // Verificar si es 00:00 o vacío
      return valor !== '' && valor !== '00:00' && valor !== '0:00' && valor !== '0';
    }
    
    return true; // Por defecto asumir que tiene horas
  }

  /**
   * Muestra confirmación para seleccionar día sin horas
   */
  private async confirmarSeleccionSinHoras(): Promise<boolean> {
    const result = await AlertUtils.fire({
      title: '⚠️ Día sin horas',
      text: 'Este día no tiene horas registradas. ¿Deseas agregarlo igualmente?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, agregar',
      cancelButtonText: 'No, cancelar',
      customClass: {
        container: 'swal-high-z-index'
      }
    });
    
    return result.isConfirmed;
  }

  private async activateSelectionMode(firstDiaId: number, firstRow: HTMLElement): Promise<void> {
    this.isSelectionMode = true;
    
    // Verificar si el primer día tiene horas
    const tieneHoras = await this.verificarDiaTieneHoras(firstRow);
    
    if (!tieneHoras) {
      const confirmado = await this.confirmarSeleccionSinHoras();
      if (!confirmado) {
        this.isSelectionMode = false;
        return; // No activar modo selección
      }
    }
    
    this.selectedRows.add(firstDiaId);
    firstRow.classList.add('row-selected');
    
    // Notificar cambio de modo
    this.options.onModeChange?.(true);
    this.options.onSelectionChange?.(this.selectedRows);
    
    // Agregar clase al tbody para visual feedback
    const tbody = this.table?.querySelector('tbody');
    if (tbody) {
      tbody.classList.add('selection-mode-active');
    }
  }

  private async toggleRowSelection(diaId: number, row: HTMLElement): Promise<void> {
    if (this.selectedRows.has(diaId)) {
      // Deseleccionar
      this.selectedRows.delete(diaId);
      row.classList.remove('row-selected');
      
      // Si no quedan días seleccionados, desactivar modo selección
      if (this.selectedRows.size === 0) {
        this.exitSelectionMode();
        return;
      }
    } else {
      // Seleccionar - verificar si tiene horas
      const tieneHoras = await this.verificarDiaTieneHoras(row);
      
      if (!tieneHoras) {
        // Mostrar confirmación
        const confirmado = await this.confirmarSeleccionSinHoras();
        if (!confirmado) {
          return; // No agregar a la selección
        }
      }
      
      this.selectedRows.add(diaId);
      row.classList.add('row-selected');
    }
    
    this.options.onSelectionChange?.(this.selectedRows);
  }

  public exitSelectionMode(): void {
    this.isSelectionMode = false;
    this.selectedRows.clear();
    
    // Remover clases de selección
    const rows = this.table?.querySelectorAll('.row-selected');
    rows?.forEach(row => row.classList.remove('row-selected'));
    
    const tbody = this.table?.querySelector('tbody');
    if (tbody) {
      tbody.classList.remove('selection-mode-active');
    }
    
    this.options.onModeChange?.(false);
    this.options.onSelectionChange?.(this.selectedRows);
  }

  public getSelectedIds(): number[] {
    return Array.from(this.selectedRows);
  }

  public isActive(): boolean {
    return this.isSelectionMode;
  }

  public destroy(): void {
    this.cancelHoldTimer();
    this.exitSelectionMode();
  }

  public refresh(): void {
    // Re-adjuntar event listeners después de que la tabla se re-renderice
    this.attachEventListeners();
  }
}
