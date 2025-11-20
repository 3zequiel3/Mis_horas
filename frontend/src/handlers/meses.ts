// Gestión de meses: cargar, navegar y crear meses del proyecto

import { ProyectoService } from '../services/proyecto';
import { AlertUtils } from '../utils/swal';
import { MESES_ES } from '../utils/formatters';

export const MesesHandler = {
  mesesDisponibles: [] as [number, number][],

  // Carga meses disponibles del proyecto
  async loadMeses(proyectoId: number) {
    try {
      this.mesesDisponibles = await ProyectoService.getMeses(proyectoId);
      this.renderMeses();
    } catch (error) {
      console.error('Error cargando meses:', error);
    }
  },

  // Verifica si un mes ya existe
  mesYaExiste(anio: number, mes: number): boolean {
    return this.mesesDisponibles.some(([a, m]) => a === anio && m === mes);
  },

  // Renderiza lista de meses y agrega event listeners
  renderMeses(mesActivo?: { anio: number; mes: number }) {
    const mesesList = document.getElementById('meses-list');
    if (!mesesList) return;

    if (this.mesesDisponibles.length === 0) {
      mesesList.innerHTML = '<div class="mes-item">Sin meses</div>';
      return;
    }

    mesesList.innerHTML = this.mesesDisponibles
      .map(([anio, mes]) => {
        const mesNombre = MESES_ES[mes as keyof typeof MESES_ES];
        const isActive = mesActivo && mesActivo.anio === anio && mesActivo.mes === mes;

        return `
          <div class="mes-item ${isActive ? 'active' : ''}" data-anio="${anio}" data-mes="${mes}">
            <span>${mesNombre} ${anio}</span>
            <span class="mes-badge">${anio}</span>
          </div>
        `;
      })
      .join('');

    // Agregar event listeners
    mesesList.querySelectorAll('.mes-item').forEach((element) => {
      element.addEventListener('click', async (e) => {
        const anio = parseInt(element.getAttribute('data-anio') || '0');
        const mes = parseInt(element.getAttribute('data-mes') || '0');

        if (anio > 0 && mes > 0) {
          const event = new CustomEvent('mes-selected', { detail: { anio, mes } });
          document.dispatchEvent(event);
        }
      });
    });
  },

  // Actualiza el texto mostrado del mes actual
  updateMesInfo(mesActivo: { anio: number; mes: number }) {
    const mesInfo = document.getElementById('mes-info');
    const mesInfoText = document.getElementById('mes-info-text');

    const mesNombre = MESES_ES[mesActivo.mes as keyof typeof MESES_ES];
    const text = `${mesNombre} ${mesActivo.anio}`;

    if (mesInfoText) mesInfoText.textContent = text;
    if (mesInfo) mesInfo.style.display = 'block';
  },

  // Abre modal para agregar nuevo mes
  openAddMesModal() {
    const modal = document.getElementById('add-mes-modal');
    if (modal) {
      modal.classList.add('show');

      // Pre-rellenar el año y mes actual + 1
      const hoy = new Date();
      let proximoMes = hoy.getMonth() + 2; // +1 para siguiente mes, +1 para 0-indexed
      let proximoAnio = hoy.getFullYear();

      if (proximoMes > 12) {
        proximoMes = 1;
        proximoAnio++;
      }

      const yearInput = document.getElementById('nuevo-mes-year') as HTMLInputElement;
      const mesInput = document.getElementById('nuevo-mes-mes') as HTMLSelectElement;

      if (yearInput) yearInput.value = proximoAnio.toString();
      if (mesInput) mesInput.value = proximoMes.toString();
    }
  },

  // Cierra modal de agregar mes
  closeAddMesModal() {
    const modal = document.getElementById('add-mes-modal');
    if (modal) {
      modal.classList.remove('show');
    }
  },

  // Agrega un nuevo mes al proyecto
  async agregarMes(proyectoId: number, anio: number, mes: number) {
    try {
      await ProyectoService.addMes(proyectoId, anio, mes);

      this.closeAddMesModal();
      await AlertUtils.success('Éxito', 'Mes agregado correctamente');

      // Recargar meses
      await this.loadMeses(proyectoId);
    } catch (error) {
      console.error('Error agregando mes:', error);
      await AlertUtils.error('Error', 'No se pudo agregar el mes');
    }
  },

  // Crea mes automáticamente si no existe
  async crearMesAutomatico(proyectoId: number, anio: number, mes: number): Promise<boolean> {
    try {
      if (this.mesYaExiste(anio, mes)) {
        return true;
      }

      // Crear el mes automáticamente
      await ProyectoService.addMes(proyectoId, anio, mes);

      // Recargar la lista de meses
      await this.loadMeses(proyectoId);
      return true;
    } catch (error) {
      console.error('Error creando mes automáticamente:', error);
      return false;
    }
  },
};
