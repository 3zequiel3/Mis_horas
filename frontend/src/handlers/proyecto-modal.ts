/**
 * Handler para el modal de creación de proyectos
 * Gestiona la apertura, cierre y creación de proyectos desde el navbar
 */

import { ProyectosService } from '../services/proyectos';
import { AlertUtils } from '../utils/swal';
import type { Proyecto } from '../types';

export const ProyectoModalHandler = {
  modal: null as HTMLElement | null,
  form: null as HTMLFormElement | null,
  
  /**
   * Inicializa el modal y sus eventos
   */
  init() {
    this.modal = document.getElementById('modal-nuevo-proyecto');
    this.form = document.getElementById('modal-proyecto-form') as HTMLFormElement;
    
    if (!this.modal || !this.form) return;

    // Inicializar selectores
    this.inicializarAnios();
    this.inicializarMes();
    this.setupEventListeners();
  },

  /**
   * Configura todos los event listeners
   */
  setupEventListeners() {
    // Botón para abrir modal desde navbar
    const openBtn = document.getElementById('open-nuevo-proyecto-modal');
    openBtn?.addEventListener('click', (e) => {
      e.preventDefault();
      this.openModal();
    });

    // Botón de cerrar
    const closeBtn = document.getElementById('close-modal-proyecto');
    closeBtn?.addEventListener('click', () => this.closeModal());

    // Botón cancelar
    const cancelBtn = document.getElementById('modal-cancel-btn');
    cancelBtn?.addEventListener('click', () => this.closeModal());

    // Cerrar al hacer clic fuera del modal
    this.modal?.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.closeModal();
      }
    });

    // Manejo de tipo de proyecto
    const tipoProyectoSelect = document.getElementById('modal-tipo-proyecto') as HTMLSelectElement;
    const empleadosContainer = document.getElementById('modal-empleados-container') as HTMLElement;
    
    tipoProyectoSelect?.addEventListener('change', () => {
      if (tipoProyectoSelect.value === 'empleados') {
        empleadosContainer.style.display = 'block';
      } else {
        empleadosContainer.style.display = 'none';
      }
    });

    // Agregar empleado
    const addEmpleadoBtn = document.getElementById('modal-add-empleado-btn');
    addEmpleadoBtn?.addEventListener('click', () => this.agregarEmpleado());

    // Eliminar primer empleado
    document.querySelectorAll('.btn-remove-empleado').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        target.closest('.empleado-item')?.remove();
      });
    });

    // Submit del formulario
    this.form?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.crearProyecto();
    });
  },

  /**
   * Llena el select de años con un rango de -5 a +5 desde actual
   */
  inicializarAnios() {
    const anioSelect = document.getElementById('modal-anio') as HTMLSelectElement;
    if (!anioSelect) return;

    const currentYear = new Date().getFullYear();
    anioSelect.innerHTML = '<option value="">Selecciona un año</option>';

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
    const mesSelect = document.getElementById('modal-mes') as HTMLSelectElement;
    if (!mesSelect) return;
    
    const currentMonth = new Date().getMonth() + 1;
    mesSelect.value = currentMonth.toString();
  },

  /**
   * Agrega un nuevo campo de empleado
   */
  agregarEmpleado() {
    const empleadosList = document.getElementById('modal-empleados-list');
    if (!empleadosList) return;

    const empleadoItem = document.createElement('div');
    empleadoItem.className = 'empleado-item';
    empleadoItem.innerHTML = `
      <input type="text" class="empleado-input" placeholder="Nombre del empleado" maxlength="100" />
      <button type="button" class="btn-remove-empleado">Eliminar</button>
    `;
    
    empleadosList.appendChild(empleadoItem);

    // Agregar evento de eliminar
    const removeBtn = empleadoItem.querySelector('.btn-remove-empleado');
    removeBtn?.addEventListener('click', () => {
      empleadoItem.remove();
    });
  },

  /**
   * Abre el modal
   */
  openModal() {
    if (this.modal) {
      this.modal.style.display = 'flex';
      this.resetForm();
    }
  },

  /**
   * Cierra el modal
   */
  closeModal() {
    if (this.modal) {
      this.modal.style.display = 'none';
      this.resetForm();
    }
  },

  /**
   * Resetea el formulario
   */
  resetForm() {
    this.form?.reset();
    this.inicializarAnios();
    this.inicializarMes();
    
    // Ocultar empleados
    const empleadosContainer = document.getElementById('modal-empleados-container');
    if (empleadosContainer) {
      empleadosContainer.style.display = 'none';
    }

    // Limpiar empleados extra
    const empleadosList = document.getElementById('modal-empleados-list');
    if (empleadosList) {
      const items = empleadosList.querySelectorAll('.empleado-item');
      items.forEach((item, index) => {
        if (index > 0) item.remove(); // Mantener solo el primero
        else {
          const input = item.querySelector('.empleado-input') as HTMLInputElement;
          if (input) input.value = '';
        }
      });
    }
  },

  /**
   * Valida el formulario
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
   * Crea el proyecto y redirige
   */
  async crearProyecto() {
    try {
      const nombre = (document.getElementById('modal-nombre') as HTMLInputElement).value;
      const anio = parseInt((document.getElementById('modal-anio') as HTMLSelectElement).value);
      const mes = parseInt((document.getElementById('modal-mes') as HTMLSelectElement).value);
      const descripcion = (document.getElementById('modal-descripcion') as HTMLTextAreaElement).value;
      const tipoProyecto = (document.getElementById('modal-tipo-proyecto') as HTMLSelectElement)?.value || 'personal';
      const horasRealesActivas = false; // Por defecto false, se activa desde configuración

      // Validar
      if (!this.validarFormulario(nombre, anio, mes)) {
        return;
      }

      // Obtener empleados si es proyecto con empleados
      let empleados: string[] = [];
      if (tipoProyecto === 'empleados') {
        const empleadosInputs = document.querySelectorAll('#modal-empleados-list .empleado-input') as NodeListOf<HTMLInputElement>;
        empleados = Array.from(empleadosInputs)
          .map(input => input.value
            .replace(/[\r\n\t]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
          )
          .filter(nombre => nombre !== '');

        if (empleados.length === 0) {
          await AlertUtils.error('Error', 'Debes agregar al menos un empleado');
          return;
        }
      }

      // Mostrar loading
      AlertUtils.loading('Creando tablero...', 'Por favor espera');

      // Crear proyecto
      const proyecto: Proyecto = await ProyectosService.createProyecto({
        nombre,
        anio,
        mes,
        descripcion: descripcion || undefined,
        tipo_proyecto: tipoProyecto as 'personal' | 'empleados',
        empleados: empleados.length > 0 ? empleados : undefined,
        horas_reales_activas: horasRealesActivas,
      });

      // Cerrar loading y mostrar éxito
      await AlertUtils.fire({
        title: '¡Tablero creado!',
        text: 'Redirigiendo al tablero...',
        icon: 'success',
        timer: 1500,
        showConfirmButton: false,
      });

      // Cerrar modal
      this.closeModal();

      // Redirigir al proyecto creado
      window.location.href = `/proyecto/${proyecto.id}`;
      
    } catch (error) {
      console.error('Error:', error);
      await AlertUtils.error('Error', 'No se pudo crear el tablero. Intenta nuevamente.');
    }
  },
};
