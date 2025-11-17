/**
 * Handler de Proyecto - Gestión de creación de proyectos
 * Incluye: crear proyecto, llenar años/meses
 */

import { ProyectosService } from '../services/proyectos';
import { AlertUtils } from '../utils/swal';

export const ProyectoFormHandler = {
  /**
   * Llena el select de años con un rango
   */
  inicializarAnios() {
    const anioSelect = document.getElementById('anio') as HTMLSelectElement;
    const currentYear = new Date().getFullYear();

    for (let i = currentYear - 5; i <= currentYear + 5; i++) {
      const option = document.createElement('option');
      option.value = i.toString();
      option.textContent = i.toString();
      if (i === currentYear) option.selected = true;
      anioSelect.appendChild(option);
    }
  },

  /**
   * Selecciona el mes actual por defecto
   */
  inicializarMes() {
    const mesSelect = document.getElementById('mes') as HTMLSelectElement;
    const currentMonth = new Date().getMonth() + 1;
    mesSelect.value = currentMonth.toString();
  },

  /**
   * Valida los datos del formulario
   */
  validarFormulario(nombre: string, anio: number, mes: number): boolean {
    if (!nombre.trim()) {
      AlertUtils.error('Error', 'El nombre del proyecto es requerido');
      return false;
    }

    if (!anio || !mes) {
      AlertUtils.error('Error', 'Por favor selecciona un año y mes válidos');
      return false;
    }

    return true;
  },

  /**
   * Crea un nuevo proyecto
   */
  async crearProyecto() {
    try {
      const nombre = (document.getElementById('nombre') as HTMLInputElement).value;
      const anio = parseInt((document.getElementById('anio') as HTMLSelectElement).value);
      const mes = parseInt((document.getElementById('mes') as HTMLSelectElement).value);
      const descripcion = (document.getElementById('descripcion') as HTMLTextAreaElement).value;

      // Validar
      if (!this.validarFormulario(nombre, anio, mes)) {
        return false;
      }

      // Crear proyecto
      await ProyectosService.createProyecto({
        nombre,
        anio,
        mes,
        descripcion: descripcion || undefined,
      });

      // Mostrar éxito
      this.mostrarMensajeExito();
      return true;
    } catch (error) {
      console.error('Error:', error);
      this.mostrarMensajeError();
      await AlertUtils.error('Error', 'No se pudo crear el proyecto. Intenta nuevamente.');
      return false;
    }
  },

  /**
   * Muestra mensaje de éxito y redirige
   */
  mostrarMensajeExito() {
    const successMsg = document.getElementById('success-message');
    if (successMsg) {
      successMsg.style.display = 'block';
      setTimeout(() => {
        window.location.href = '/proyectos';
      }, 1500);
    }
  },

  /**
   * Muestra mensaje de error
   */
  mostrarMensajeError() {
    const errorMsg = document.getElementById('error-message');
    if (errorMsg) {
      errorMsg.style.display = 'block';
      setTimeout(() => {
        errorMsg.style.display = 'none';
      }, 5000);
    }
  },
};
