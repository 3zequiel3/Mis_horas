// Gestión de creación de proyectos: datos, años, meses

import { ProyectosService } from '../services/proyectos';
import { initializeOrganizationContext } from '../utils/organizationContext';
import { AlertUtils } from '../utils/swal';

export const ProyectoFormHandler = {
  // FASE 1 MULTI-TENANT: Inicializa el contexto organizacional
  async inicializar() {
    try {
      await initializeOrganizationContext();
    } catch (error) {
      console.error('Error inicializando contexto organizacional:', error);
    }
  },
  
  // Llena el select de años con un rango de -5 a +5 desde actual
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

  // Selecciona el mes actual en el select por defecto
  inicializarMes() {
    const mesSelect = document.getElementById('mes') as HTMLSelectElement;
    const currentMonth = new Date().getMonth() + 1;
    mesSelect.value = currentMonth.toString();
  },

  // Valida que el nombre, año y mes sean válidos
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

  // Crea un nuevo proyecto en el servidor
  async crearProyecto() {
    try {
      const nombre = (document.getElementById('nombre') as HTMLInputElement).value;
      const anio = parseInt((document.getElementById('anio') as HTMLSelectElement).value);
      const mes = parseInt((document.getElementById('mes') as HTMLSelectElement).value);
      const descripcion = (document.getElementById('descripcion') as HTMLTextAreaElement).value;
      const tipoProyecto = (document.getElementById('tipo_proyecto') as HTMLSelectElement)?.value || 'personal';
      const horasRealesActivas = false; // Por defecto false, se activa desde configuración

      // FASE 4: Nuevos campos
      const cliente = (document.getElementById('cliente') as HTMLInputElement)?.value || undefined;
      const brandColor = (document.getElementById('brand_color') as HTMLInputElement)?.value || undefined;
      const modulesConfigStr = (document.getElementById('modules_config') as HTMLInputElement)?.value || '{}';
      const modulesConfig = JSON.parse(modulesConfigStr);

      // FASE 4: Configuración financiera
      const budgetTypeValue = (document.getElementById('budget_type') as HTMLInputElement)?.value || 'none';
      const budgetType = budgetTypeValue as 'none' | 'fixed_price' | 'hourly_retainer' | 'time_and_materials';
      const budgetBaseAmountStr = (document.getElementById('budget_base_amount') as HTMLInputElement)?.value;
      const budgetBaseAmount = budgetBaseAmountStr ? parseFloat(budgetBaseAmountStr) : undefined;
      const currency = (document.getElementById('currency') as HTMLSelectElement)?.value || 'USD';

      // Validar
      if (!this.validarFormulario(nombre, anio, mes)) {
        return false;
      }

      // Obtener empleados si es proyecto con empleados
      let empleados: string[] = [];
      let empleadosEmails: { [nombre: string]: string } = {};
      
      if (tipoProyecto === 'empleados') {
        const empleadosItems = document.querySelectorAll('.empleado-item');
        
        empleadosItems.forEach(item => {
          const nombreInput = item.querySelector('.empleado-nombre') as HTMLInputElement;
          const emailInput = item.querySelector('.empleado-email') as HTMLInputElement;
          
          if (nombreInput && nombreInput.value.trim()) {
            const nombre = nombreInput.value
              .replace(/[\r\n\t]/g, ' ')
              .replace(/\s+/g, ' ')
              .trim();
            
            empleados.push(nombre);
            
            // Si tiene email asociado, guardarlo
            if (emailInput && emailInput.value.trim()) {
              empleadosEmails[nombre] = emailInput.value.trim();
            }
          }
        });

        if (empleados.length === 0) {
          await AlertUtils.error('Error', 'Debes agregar al menos un empleado');
          return false;
        }
      }

      // Crear proyecto
      await ProyectosService.createProyecto({
        nombre,
        anio,
        mes,
        descripcion: descripcion || undefined,
        tipo_proyecto: tipoProyecto as 'personal' | 'empleados',
        empleados: empleados.length > 0 ? empleados : undefined,
        horas_reales_activas: horasRealesActivas,
        // FASE 4: Nuevos campos
        client_name: cliente,
        brand_color: brandColor,
        modules_config: modulesConfig,
        budget_type: budgetType,
        budget_base_amount: budgetBaseAmount,
        currency: currency,
        // Los horarios se configurarán opcionalmente después desde el drawer
      });

      // Mostrar éxito
      this.mostrarMensajeExito();
      return true;
    } catch (error) {
      console.error('Error:', error);
      this.mostrarMensajeError();
      await AlertUtils.error('Error', 'No se pudo crear el tablero. Intenta nuevamente.');
      return false;
    }
  },

  // Muestra mensaje de éxito y redirige a proyectos
  mostrarMensajeExito() {
    const successMsg = document.getElementById('success-message');
    if (successMsg) {
      successMsg.style.display = 'block';
      setTimeout(() => {
        window.location.href = '/proyectos';
      }, 1500);
    }
  },

  // Muestra mensaje de error en pantalla
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
