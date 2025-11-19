// Gestión de tareas: crear, editar, eliminar y días asignados

import { TareaService } from '../services/tarea';
import { AlertUtils } from '../utils/swal';
import { horasAFormato } from '../utils/formatters';

export interface DiasInfo {
  id: number;
  fecha: string;
  texto: string;
}

export const TareaHandler = {
  diasSeleccionados: new Map<number, DiasInfo>(),
  diasDisponibles: new Map<number, DiasInfo>(),
  tareaEnVista: null as any,

  // Actualiza select de días (solo muestra los no seleccionados)
  actualizarSelectDias(diasSelect: HTMLSelectElement) {
    diasSelect.innerHTML = '<option value="">Seleccione los días</option>';

    this.diasDisponibles.forEach((dia) => {
      if (!this.diasSeleccionados.has(dia.id)) {
        const option = document.createElement('option');
        option.value = dia.id.toString();
        option.textContent = dia.texto;
        diasSelect.appendChild(option);
      }
    });
  },

  // Renderiza badges de días seleccionados
  renderizarDiasSeleccionados(diasSelectedDiv: HTMLElement) {
    if (this.diasSeleccionados.size === 0) {
      diasSelectedDiv.innerHTML = '';
      return;
    }

    diasSelectedDiv.innerHTML = Array.from(this.diasSeleccionados.values())
      .map(
        (dia) => `
      <div class="dia-badge">
        <span>${dia.texto}</span>
        <button type="button" class="dia-remove" data-dia-id="${dia.id}">✕</button>
      </div>
    `
      )
      .join('');

    diasSelectedDiv.querySelectorAll('.dia-remove').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const diaId = parseInt((btn as HTMLElement).getAttribute('data-dia-id') || '0');
        this.diasSeleccionados.delete(diaId);
        const diasSelect = document.getElementById('dias-select') as HTMLSelectElement;
        if (diasSelect) this.actualizarSelectDias(diasSelect);
        this.renderizarDiasSeleccionados(diasSelectedDiv);
      });
    });
  },

  // Carga días disponibles para asignar a tarea
  async loadDiasDisponibles(
    proyectoId: number,
    anio: number,
    mes: number,
    tareaId?: number
  ) {
    try {
      const dias = await TareaService.getDiasDisponibles(proyectoId, anio, mes, tareaId);

      this.diasDisponibles.clear();

      dias.forEach((dia: any) => {
        const fechaFormato = new Date(dia.fecha).toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          weekday: 'short',
        });

        this.diasDisponibles.set(dia.id, {
          id: dia.id,
          fecha: dia.fecha,
          texto: fechaFormato,
        });
      });

      const diasSelect = document.getElementById('dias-select') as HTMLSelectElement;
      if (diasSelect) this.actualizarSelectDias(diasSelect);
    } catch (error) {
      console.error('Error cargando días:', error);
      const diasSelect = document.getElementById('dias-select') as HTMLSelectElement;
      if (diasSelect) diasSelect.innerHTML = '<option disabled>Error al cargar días</option>';
    }
  },

  // Limpia formulario para crear nueva tarea
  resetParaCrear(form: HTMLFormElement, preselectedDiaIds?: number[]) {
    form.reset();
    this.diasSeleccionados.clear();

    const modalTitle = document.getElementById('modal-title');
    const submitBtn = form.querySelector<HTMLButtonElement>('button[type="submit"]');

    if (modalTitle) modalTitle.textContent = 'Nueva Tarea';
    if (submitBtn) {
      submitBtn.textContent = 'Crear Tarea';
      submitBtn.dataset.editMode = 'false';
      submitBtn.dataset.tareaId = '0';
    }

    // Pre-seleccionar días si se proporcionan
    if (preselectedDiaIds && preselectedDiaIds.length > 0) {
      preselectedDiaIds.forEach((diaId) => {
        const dia = this.diasDisponibles.get(diaId);
        if (dia) {
          this.diasSeleccionados.set(diaId, dia);
        }
      });

      const diasSelect = document.getElementById('dias-select') as HTMLSelectElement;
      if (diasSelect) this.actualizarSelectDias(diasSelect);
    }

    const diasSelectedDiv = document.getElementById('dias-selected')!;
    this.renderizarDiasSeleccionados(diasSelectedDiv);
  },

  // Prepara formulario para editar una tarea existente
  async cargarParaEditar(tarea: any, proyectoId: number, anio: number, mes: number) {
    const form = document.getElementById('tarea-form') as HTMLFormElement;
    const modalTitle = document.getElementById('modal-title');

    if (modalTitle) {
      modalTitle.textContent = `Editar Tarea: ${tarea.titulo}`;
    }

    (document.getElementById('tarea-titulo') as HTMLInputElement).value = tarea.titulo;
    (document.getElementById('tarea-detalle') as HTMLTextAreaElement).value = tarea.detalle || '';
    (document.getElementById('tarea-que-falta') as HTMLTextAreaElement).value = tarea.que_falta || '';

    // Cargar días disponibles (excluyendo esta tarea)
    await this.loadDiasDisponibles(proyectoId, anio, mes, tarea.id);

    // Cargar días seleccionados de la tarea actual
    this.diasSeleccionados.clear();
    if (tarea.dias && Array.isArray(tarea.dias)) {
      tarea.dias.forEach((dia: any) => {
        const fechaFormato = new Date(dia.fecha).toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          weekday: 'short',
        });

        this.diasSeleccionados.set(dia.id, {
          id: dia.id,
          fecha: dia.fecha,
          texto: fechaFormato,
        });
      });
    }

    const diasSelect = document.getElementById('dias-select') as HTMLSelectElement;
    if (diasSelect) this.actualizarSelectDias(diasSelect);

    const diasSelectedDiv = document.getElementById('dias-selected')!;
    this.renderizarDiasSeleccionados(diasSelectedDiv);

    // Cambiar botón submit a modo edición
    const submitBtn = form.querySelector<HTMLButtonElement>('button[type="submit"]');
    if (submitBtn) {
      submitBtn.textContent = 'Guardar cambios';
      submitBtn.dataset.editMode = 'true';
      submitBtn.dataset.tareaId = tarea.id.toString();
    }
  },

  // Guarda tarea nueva o actualiza existente
  async guardarTarea(
    form: HTMLFormElement,
    proyectoId: number,
    onSuccess: () => Promise<void>
  ): Promise<boolean> {
    try {
      const titulo = (document.getElementById('tarea-titulo') as HTMLInputElement).value;
      const detalle = (document.getElementById('tarea-detalle') as HTMLTextAreaElement).value;
      const que_falta = (document.getElementById('tarea-que-falta') as HTMLTextAreaElement).value;
      const submitBtn = form.querySelector<HTMLButtonElement>('button[type="submit"]');
      const editMode = submitBtn?.dataset.editMode === 'true';
      const tareaId = parseInt(submitBtn?.dataset.tareaId || '0');

      if (!titulo.trim()) {
        await AlertUtils.error('Error', 'El título es requerido');
        return false;
      }

      const diasIds = Array.from(this.diasSeleccionados.keys());

      if (editMode && tareaId > 0) {
        await TareaService.updateTarea(tareaId, titulo, detalle, que_falta, diasIds);
        await AlertUtils.success('Éxito', 'Tarea actualizada correctamente');
      } else {
        await TareaService.createTarea(
          proyectoId,
          titulo,
          detalle,
          que_falta,
          diasIds.length > 0 ? diasIds : undefined
        );
        await AlertUtils.success('Éxito', 'Tarea creada correctamente');
      }

      form.reset();
      this.diasSeleccionados.clear();
      const diasSelectedDiv = document.getElementById('dias-selected')!;
      diasSelectedDiv.innerHTML = '';

      if (submitBtn) {
        submitBtn.textContent = 'Crear Tarea';
        submitBtn.dataset.editMode = 'false';
        submitBtn.dataset.tareaId = '0';
      }

      await onSuccess();
      return true;
    } catch (error) {
      console.error('Error con tarea:', error);
      await AlertUtils.error('Error', 'No se pudo guardar la tarea');
      return false;
    }
  },

  // Renderiza detalles completos de una tarea
  renderizarVistaDetalle(tarea: any, usuarioUsaHorasReales: boolean) {
    const viewModalBody = document.getElementById('view-modal-body');
    const viewModalTitle = document.getElementById('view-modal-title');

    if (viewModalTitle) {
      viewModalTitle.textContent = tarea.titulo;
    }

    if (viewModalBody) {
      // Usar las horas ya calculadas por el backend (respeta tipo de proyecto y configuración)
      const horasTexto = tarea.horas || '00:00';
      // Convertir "HH:MM" a número de horas para mostrar
      const [horas, minutos] = horasTexto.split(':').map(Number);
      const horasTotales = horas + (minutos / 60);
      
      let diasHtml = '';
      let desgloseEmpleadosHtml = '';

      if (tarea.dias && tarea.dias.length > 0) {
        diasHtml = tarea.dias
          .map((d: any) => {
            const fecha = new Date(d.fecha).toLocaleDateString('es-ES', {
              day: '2-digit',
              month: '2-digit',
              year: '2-digit',
              weekday: 'short',
            });

            return `
              <div class="dia-badge-item">
                <span class="dia-badge-label">${fecha}</span>
              </div>
            `;
          })
          .join('');
      } else {
        diasHtml = '<div class="dias-empty"><p>Sin días asignados</p></div>';
      }

      // Mostrar desglose por empleado si existe
      if (tarea.desglose_empleados && tarea.desglose_empleados.length > 0) {
        desgloseEmpleadosHtml = `
          <div class="detalle-seccion">
            <div class="seccion-header">
              <h4 class="seccion-titulo">👥 Horas por Empleado</h4>
            </div>
            <div class="desglose-empleados">
              ${tarea.desglose_empleados.map((emp: any) => {
                const horas = horasAFormato(emp.horas_totales);
                return `
                  <div class="empleado-desglose-item">
                    <span class="empleado-desglose-nombre">${emp.empleado_nombre}</span>
                    <span class="empleado-desglose-horas">${horas}</span>
                    <span class="empleado-desglose-dias">${emp.dias_count} día${emp.dias_count !== 1 ? 's' : ''}</span>
                  </div>
                `;
              }).join('')}
            </div>
          </div>
        `;
      }

      viewModalBody.innerHTML = `
        <div class="tarea-detalle-mejorada">
          <div class="detalle-seccion">
            <div class="seccion-header">
              <h4 class="seccion-titulo">📝 Detalle</h4>
            </div>
            <p class="seccion-contenido">${tarea.detalle || 'Sin detalle'}</p>
          </div>

          <div class="detalle-seccion">
            <div class="seccion-header">
              <h4 class="seccion-titulo">❓ ¿Qué falta?</h4>
            </div>
            <p class="seccion-contenido">${tarea.que_falta || 'Nada pendiente'}</p>
          </div>

          <div class="detalle-seccion">
            <div class="seccion-header">
              <h4 class="seccion-titulo">⏱️ Horas totales</h4>
            </div>
            <div class="horas-totales-badge">
              <span class="horas-numero">${horasTotales}h</span>
              <span class="horas-label">Acumuladas</span>
            </div>
          </div>

          ${desgloseEmpleadosHtml}

          <div class="detalle-seccion">
            <div class="seccion-header">
              <h4 class="seccion-titulo">📅 Días asignados</h4>
            </div>
            <div class="dias-desglose-inline">
              ${diasHtml}
            </div>
          </div>
        </div>
      `;
    }
  },

  // Elimina una tarea después de confirmación
  async eliminarTarea(tareaId: number, nombreTarea: string, onSuccess: () => Promise<void>) {
    const result = await AlertUtils.confirm(
      '¿Eliminar tarea?',
      `Se eliminará la tarea "${nombreTarea}" y sus días volverán a estar disponibles`,
      'Sí, eliminar',
      'Cancelar'
    );

    if (result.isConfirmed) {
      try {
        await TareaService.deleteTarea(tareaId);
        await AlertUtils.success('Eliminada', 'La tarea ha sido eliminada correctamente');
        await onSuccess();
      } catch (error) {
        console.error('Error eliminando tarea:', error);
        await AlertUtils.error('Error', 'No se pudo eliminar la tarea');
      }
    }
  },
};
