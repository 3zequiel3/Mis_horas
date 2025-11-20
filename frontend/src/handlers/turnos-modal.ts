/**
 * Handler para el modal de turnos
 * Gestiona la apertura, cierre y guardado de horarios por turnos
 */

import { ApiService } from '../services/api';
import type { Proyecto } from '../types/Proyecto';

interface TurnosData {
  diaId: number;
  empleadoNombre: string;
  fecha: string;
  turnoMananaEntrada?: string;
  turnoMananaSalida?: string;
  turnoTardeEntrada?: string;
  turnoTardeSalida?: string;
}

export const TurnosModalHandler = {
  proyecto: null as Proyecto | null,

  /**
   * Inicializa el modal de turnos
   */
  init(proyecto: Proyecto) {
    this.proyecto = proyecto;
    this.setupEventListeners();
  },

  /**
   * Configura los event listeners del modal
   */
  setupEventListeners() {
    const modal = document.getElementById('turnos-modal');
    const closeBtn = document.getElementById('close-turnos-modal');
    const cancelBtn = document.getElementById('cancel-turnos-modal');
    const form = document.getElementById('turnos-form') as HTMLFormElement;

    closeBtn?.addEventListener('click', () => this.cerrarModal());
    cancelBtn?.addEventListener('click', () => this.cerrarModal());

    // Cerrar al hacer click fuera del modal
    modal?.addEventListener('click', (e) => {
      if (e.target === modal) {
        this.cerrarModal();
      }
    });

    // Calcular subtotales en tiempo real
    const inputs = [
      'turno_manana_entrada',
      'turno_manana_salida',
      'turno_tarde_entrada',
      'turno_tarde_salida',
    ];

    inputs.forEach((id) => {
      document.getElementById(id)?.addEventListener('change', () => {
        this.calcularTotales();
      });
    });

    // Enviar formulario
    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.guardarTurnos();
    });
  },

  /**
   * Abre el modal con los datos del día
   */
  abrirModal(data: TurnosData) {
    const modal = document.getElementById('turnos-modal');
    if (!modal) return;

    // Llenar información del empleado y fecha
    const empleadoNombre = document.getElementById('modal-empleado-nombre');
    const fecha = document.getElementById('modal-fecha');
    const diaId = document.getElementById('modal-dia-id') as HTMLInputElement;

    if (empleadoNombre) empleadoNombre.textContent = data.empleadoNombre;
    if (fecha) fecha.textContent = this.formatearFecha(data.fecha);
    if (diaId) diaId.value = data.diaId.toString();

    // Llenar valores existentes
    const mananaEntrada = document.getElementById('turno_manana_entrada') as HTMLInputElement;
    const mananaSalida = document.getElementById('turno_manana_salida') as HTMLInputElement;
    const tardeEntrada = document.getElementById('turno_tarde_entrada') as HTMLInputElement;
    const tardeSalida = document.getElementById('turno_tarde_salida') as HTMLInputElement;

    if (mananaEntrada) mananaEntrada.value = data.turnoMananaEntrada || '';
    if (mananaSalida) mananaSalida.value = data.turnoMananaSalida || '';
    if (tardeEntrada) tardeEntrada.value = data.turnoTardeEntrada || '';
    if (tardeSalida) tardeSalida.value = data.turnoTardeSalida || '';

    // Calcular totales iniciales
    this.calcularTotales();

    // Mostrar modal
    modal.style.display = 'flex';
  },

  /**
   * Cierra el modal
   */
  cerrarModal() {
    const modal = document.getElementById('turnos-modal');
    if (modal) {
      modal.style.display = 'none';
    }
  },

  /**
   * Calcula y muestra los totales de horas
   */
  calcularTotales() {
    const mananaEntrada = (document.getElementById('turno_manana_entrada') as HTMLInputElement)?.value;
    const mananaSalida = (document.getElementById('turno_manana_salida') as HTMLInputElement)?.value;
    const tardeEntrada = (document.getElementById('turno_tarde_entrada') as HTMLInputElement)?.value;
    const tardeSalida = (document.getElementById('turno_tarde_salida') as HTMLInputElement)?.value;

    console.log('🔍 Valores inputs:', { mananaEntrada, mananaSalida, tardeEntrada, tardeSalida });

    const modal = document.getElementById('turnos-modal');
    if (!modal) {
      console.error('❌ No se encontró el modal');
      return;
    }

    let totalHoras = 0;

    // Calcular turno mañana (máximo las horas configuradas)
    if (mananaEntrada && mananaSalida) {
      const horasManana = this.calcularDiferenciaHoras(mananaEntrada, mananaSalida);
      console.log('📊 Horas mañana trabajadas:', horasManana);
      
      // Para el subtotal, mostrar las horas trabajadas
      const subtotalManana = modal.querySelector('#subtotal-manana') as HTMLElement;
      if (subtotalManana) subtotalManana.textContent = this.formatearHoras(horasManana);
      
      // Para el total, contar máximo las horas configuradas (sin extras)
      if (this.proyecto?.turno_manana_inicio && this.proyecto?.turno_manana_fin) {
        const horasConfiguradas = this.calcularDiferenciaHoras(this.proyecto.turno_manana_inicio, this.proyecto.turno_manana_fin);
        totalHoras += Math.min(horasManana, horasConfiguradas);
      } else {
        totalHoras += horasManana;
      }
    } else {
      const subtotalManana = modal.querySelector('#subtotal-manana') as HTMLElement;
      if (subtotalManana) subtotalManana.textContent = '0:00';
    }

    // Calcular turno tarde (máximo las horas configuradas)
    if (tardeEntrada && tardeSalida) {
      const horasTarde = this.calcularDiferenciaHoras(tardeEntrada, tardeSalida);
      console.log('📊 Horas tarde trabajadas:', horasTarde);
      
      // Para el subtotal, mostrar las horas trabajadas
      const subtotalTarde = modal.querySelector('#subtotal-tarde') as HTMLElement;
      if (subtotalTarde) subtotalTarde.textContent = this.formatearHoras(horasTarde);
      
      // Para el total, contar máximo las horas configuradas (sin extras)
      if (this.proyecto?.turno_tarde_inicio && this.proyecto?.turno_tarde_fin) {
        const horasConfiguradas = this.calcularDiferenciaHoras(this.proyecto.turno_tarde_inicio, this.proyecto.turno_tarde_fin);
        totalHoras += Math.min(horasTarde, horasConfiguradas);
      } else {
        totalHoras += horasTarde;
      }
    } else {
      const subtotalTarde = modal.querySelector('#subtotal-tarde') as HTMLElement;
      if (subtotalTarde) subtotalTarde.textContent = '0:00';
    }

    console.log('✅ Total horas calculado:', totalHoras);
    console.log('✅ Total horas formateado:', this.formatearHoras(totalHoras));

    // Mostrar total
    const totalElement = modal.querySelector('#total-horas') as HTMLElement;
    if (totalElement) {
      const valorFormateado = this.formatearHoras(totalHoras);
      totalElement.textContent = valorFormateado;
      console.log('✅ Elemento actualizado, textContent:', totalElement.textContent);
      console.log('✅ Valor asignado:', valorFormateado);
      console.log('✅ innerHTML:', totalElement.innerHTML);
    } else {
      console.error('❌ No se encontró el elemento total-horas');
    }

    // Calcular y mostrar horas extras
    // Solo cuenta como extra cuando se trabajan MÁS horas que las configuradas para el turno
    let horasExtras = 0;

    // Extras del turno mañana
    if (mananaEntrada && mananaSalida && this.proyecto?.turno_manana_inicio && this.proyecto?.turno_manana_fin) {
      const horasTrabajadas = this.calcularDiferenciaHoras(mananaEntrada, mananaSalida);
      const horasConfiguradas = this.calcularDiferenciaHoras(this.proyecto.turno_manana_inicio, this.proyecto.turno_manana_fin);
      
      // Solo hay extras si trabajó MÁS horas que las configuradas
      if (horasTrabajadas > horasConfiguradas) {
        horasExtras += (horasTrabajadas - horasConfiguradas);
      }
    }

    // Extras del turno tarde
    if (tardeEntrada && tardeSalida && this.proyecto?.turno_tarde_inicio && this.proyecto?.turno_tarde_fin) {
      const horasTrabajadas = this.calcularDiferenciaHoras(tardeEntrada, tardeSalida);
      const horasConfiguradas = this.calcularDiferenciaHoras(this.proyecto.turno_tarde_inicio, this.proyecto.turno_tarde_fin);
      
      // Solo hay extras si trabajó MÁS horas que las configuradas
      if (horasTrabajadas > horasConfiguradas) {
        horasExtras += (horasTrabajadas - horasConfiguradas);
      }
    }

    const extrasRow = modal.querySelector('#extras-row') as HTMLElement;
    const extrasValue = modal.querySelector('#horas-extras') as HTMLElement;

    if (horasExtras > 0) {
      if (extrasRow) extrasRow.style.display = 'flex';
      if (extrasValue) extrasValue.textContent = `+${this.formatearHoras(horasExtras)}`;
    } else {
      if (extrasRow) extrasRow.style.display = 'none';
    }
  },

  /**
   * Formatea horas decimales a formato HH:MM
   */
  formatearHoras(horas: number): string {
    const h = Math.floor(horas);
    const m = Math.round((horas - h) * 60);
    return `${h}:${m.toString().padStart(2, '0')}`;
  },

  /**
   * Calcula la diferencia en horas entre dos tiempos
   */
  calcularDiferenciaHoras(inicio: string, fin: string): number {
    const [hI, mI] = inicio.split(':').map(Number);
    const [hF, mF] = fin.split(':').map(Number);

    let minutosInicio = hI * 60 + mI;
    let minutosFin = hF * 60 + mF;

    // Si el fin es menor que el inicio, asumimos que cruzó medianoche
    if (minutosFin < minutosInicio) {
      minutosFin += 24 * 60;
    }

    return (minutosFin - minutosInicio) / 60;
  },

  /**
   * Valida que los campos de entrada/salida estén completos
   */
  validarRangos(): boolean {
    const mananaEntrada = (document.getElementById('turno_manana_entrada') as HTMLInputElement)?.value;
    const mananaSalida = (document.getElementById('turno_manana_salida') as HTMLInputElement)?.value;
    const tardeEntrada = (document.getElementById('turno_tarde_entrada') as HTMLInputElement)?.value;
    const tardeSalida = (document.getElementById('turno_tarde_salida') as HTMLInputElement)?.value;

    // Validar que si hay entrada, también haya salida (y viceversa)
    if ((mananaEntrada && !mananaSalida) || (!mananaEntrada && mananaSalida)) {
      alert('Debes ingresar tanto la entrada como la salida del turno mañana');
      return false;
    }

    if ((tardeEntrada && !tardeSalida) || (!tardeEntrada && tardeSalida)) {
      alert('Debes ingresar tanto la entrada como la salida del turno tarde');
      return false;
    }

    // Validar que al menos un turno esté completo
    if (!mananaEntrada && !tardeEntrada) {
      alert('Debes ingresar al menos un turno (mañana o tarde)');
      return false;
    }

    return true;
  },

  /**
   * Guarda los turnos en el servidor
   */
  async guardarTurnos() {
    if (!this.validarRangos()) {
      return;
    }

    const diaId = (document.getElementById('modal-dia-id') as HTMLInputElement)?.value;
    const mananaEntrada = (document.getElementById('turno_manana_entrada') as HTMLInputElement)?.value;
    const mananaSalida = (document.getElementById('turno_manana_salida') as HTMLInputElement)?.value;
    const tardeEntrada = (document.getElementById('turno_tarde_entrada') as HTMLInputElement)?.value;
    const tardeSalida = (document.getElementById('turno_tarde_salida') as HTMLInputElement)?.value;

    try {
      await ApiService['put'](`/api/dias/${diaId}/turnos`, {
        turno_manana_entrada: mananaEntrada || null,
        turno_manana_salida: mananaSalida || null,
        turno_tarde_entrada: tardeEntrada || null,
        turno_tarde_salida: tardeSalida || null,
      });

      this.cerrarModal();
      
      // Recargar la página para reflejar los cambios
      window.location.reload();
    } catch (error) {
      console.error('Error guardando turnos:', error);
      alert('Error al guardar los turnos. Intenta nuevamente.');
    }
  },

  /**
   * Formatea una fecha para mostrar
   */
  formatearFecha(fecha: string): string {
    const date = new Date(fecha + 'T00:00:00');
    const opciones: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return date.toLocaleDateString('es-ES', opciones);
  },
};
