// Gestión de creación de proyectos: datos, años, meses

import { ProyectosService } from '../services/proyectos';
import { AlertUtils } from '../utils/swal';

export const ProyectoFormHandler = {
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

      // Obtener configuración de turnos
      const modoHorarios = (document.getElementById('modo_horarios') as HTMLSelectElement)?.value || 'corrido';
      const horarioInicio = (document.getElementById('horario_inicio') as HTMLInputElement)?.value || undefined;
      const horarioFin = (document.getElementById('horario_fin') as HTMLInputElement)?.value || undefined;
      const turnoMananaInicio = (document.getElementById('turno_manana_inicio') as HTMLInputElement)?.value || undefined;
      const turnoMananaFin = (document.getElementById('turno_manana_fin') as HTMLInputElement)?.value || undefined;
      const turnoTardeInicio = (document.getElementById('turno_tarde_inicio') as HTMLInputElement)?.value || undefined;
      const turnoTardeFin = (document.getElementById('turno_tarde_fin') as HTMLInputElement)?.value || undefined;

      // Validar
      if (!this.validarFormulario(nombre, anio, mes)) {
        return false;
      }

      // Validar configuración de turnos si está en modo turnos
      if (modoHorarios === 'turnos') {
        if (!turnoMananaInicio || !turnoMananaFin || !turnoTardeInicio || !turnoTardeFin) {
          await AlertUtils.error('Error', 'Debes configurar los horarios de ambos turnos');
          return false;
        }
      }

      // Obtener empleados si es proyecto con empleados
      let empleados: string[] = [];
      if (tipoProyecto === 'empleados') {
        const empleadosInputs = document.querySelectorAll('.empleado-input') as NodeListOf<HTMLInputElement>;
        empleados = Array.from(empleadosInputs)
          .map(input => input.value
            .replace(/[\r\n\t]/g, ' ')  // Reemplazar saltos de línea y tabs por espacio
            .replace(/\s+/g, ' ')       // Normalizar múltiples espacios a uno solo
            .trim()                      // Eliminar espacios al inicio y final
          )
          .filter(nombre => nombre !== '');

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
        modo_horarios: modoHorarios as 'corrido' | 'turnos',
        horario_inicio: horarioInicio,
        horario_fin: horarioFin,
        turno_manana_inicio: turnoMananaInicio,
        turno_manana_fin: turnoMananaFin,
        turno_tarde_inicio: turnoTardeInicio,
        turno_tarde_fin: turnoTardeFin,
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
