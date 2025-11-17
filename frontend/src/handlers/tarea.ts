/**
 * Handlers de Tareas - Lógica completa de gestión de tareas
 * Incluye: crear, editar, eliminar, visualizar tareas y gestión de días
 */

import { TareaService } from '../services/tarea';
import { AlertUtils } from '../utils/swal';

export interface DiasInfo {
  id: number;
  fecha: string;
  texto: string;
}

export const TareaHandler = {
  // Estado
  diasSeleccionados: new Map<number, DiasInfo>(),
  diasDisponibles: new Map<number, DiasInfo>(),
  tareaEnVista: null as any,

  /**
   * Actualiza las opciones del select mostrando solo días no seleccionados
   */
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

  /**
   * Renderiza los días seleccionados como badges
   */
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

  /**
   * Carga los días disponibles para la tarea
   */
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

  /**
   * Limpia el formulario y estado para crear nueva tarea
   */
  resetParaCrear(form: HTMLFormElement) {
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

    const diasSelectedDiv = document.getElementById('dias-selected')!;
    this.renderizarDiasSeleccionados(diasSelectedDiv);
  },

  /**
   * Prepara el formulario para editar una tarea
   */
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

  /**
   * Guarda la tarea (crear o actualizar)
   */
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

  /**
   * Renderiza el modal de visualización de tarea
   */
  renderizarVistaDetalle(tarea: any, usuarioUsaHorasReales: boolean) {
    const viewModalBody = document.getElementById('view-modal-body');
    const viewModalTitle = document.getElementById('view-modal-title');

    if (viewModalTitle) {
      viewModalTitle.textContent = tarea.titulo;
    }

    if (viewModalBody) {
      let horasTotales = 0;
      let diasHtml = '';

      if (tarea.dias && tarea.dias.length > 0) {
        tarea.dias.forEach((d: any) => {
          const horasAMostrar = usuarioUsaHorasReales
            ? d.horas_reales || 0
            : d.horas_trabajadas || 0;

          horasTotales += horasAMostrar;
        });

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

  /**
   * Elimina una tarea
   */
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
