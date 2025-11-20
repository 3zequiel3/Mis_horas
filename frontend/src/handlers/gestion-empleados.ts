/**
 * Handler para gestión de empleados del tablero
 */

import Swal from 'sweetalert2';
import { EmpleadosService } from '../services/empleados';
import type { Empleado } from '../types';

export const GestionEmpleadosHandler = {
  /**
   * Mostrar panel de gestión de empleados
   */
  async mostrar(proyectoId: number, empleados: Empleado[]): Promise<void> {
    const empleadosHTML = empleados.map(emp => `
      <div class="empleado-gestion-item" style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; margin-bottom: 10px;">
        <div>
          <strong style="color: #c8c8c8; font-size: 15px;">${emp.nombre}</strong>
          ${emp.usuario_id ? '<span style="margin-left: 10px; padding: 2px 8px; background: rgba(34, 197, 94, 0.15); color: #22c55e; border-radius: 4px; font-size: 11px;">✓ Vinculado</span>' : '<span style="margin-left: 10px; padding: 2px 8px; background: rgba(156, 163, 175, 0.15); color: #9ca3af; border-radius: 4px; font-size: 11px;">Sin vincular</span>'}
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn-edit-empleado" data-id="${emp.id}" data-nombre="${emp.nombre}" style="padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">✏️ Editar</button>
          <button class="btn-delete-empleado" data-id="${emp.id}" data-nombre="${emp.nombre}" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">🗑️</button>
        </div>
      </div>
    `).join('');

    await Swal.fire({
      title: 'Gestión de Empleados',
      width: '700px',
      html: `
        <div style="text-align: left;">
          <button id="btn-agregar-empleado" style="width: 100%; padding: 12px; margin-bottom: 20px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 600;">
            ➕ Agregar Nuevo Empleado
          </button>
          
          <div style="max-height: 400px; overflow-y: auto;">
            ${empleadosHTML || '<p style="text-align: center; color: #9ca3af; padding: 40px;">No hay empleados en este tablero</p>'}
          </div>
        </div>
      `,
      showConfirmButton: false,
      showCancelButton: true,
      cancelButtonText: 'Cerrar',
      background: '#0f1419',
      color: '#c8c8c8',
      cancelButtonColor: '#2d3746',
      didOpen: () => {
        // Agregar empleado
        document.getElementById('btn-agregar-empleado')?.addEventListener('click', async () => {
          await this.agregarEmpleado(proyectoId);
        });

        // Editar empleado
        document.querySelectorAll('.btn-edit-empleado').forEach(btn => {
          btn.addEventListener('click', async (e) => {
            const target = e.target as HTMLElement;
            const empleadoId = parseInt(target.getAttribute('data-id') || '0');
            const nombreActual = target.getAttribute('data-nombre') || '';
            await this.editarEmpleado(empleadoId, nombreActual);
          });
        });

        // Eliminar empleado
        document.querySelectorAll('.btn-delete-empleado').forEach(btn => {
          btn.addEventListener('click', async (e) => {
            const target = e.target as HTMLElement;
            const empleadoId = parseInt(target.getAttribute('data-id') || '0');
            const nombreEmpleado = target.getAttribute('data-nombre') || '';
            await this.eliminarEmpleado(empleadoId, nombreEmpleado);
          });
        });
      }
    });
  },

  /**
   * Agregar nuevo empleado
   */
  async agregarEmpleado(proyectoId: number): Promise<void> {
    const { value: nombreEmpleado } = await Swal.fire({
      title: 'Agregar Empleado',
      input: 'text',
      inputLabel: 'Nombre del empleado',
      inputPlaceholder: 'Ej: Juan Pérez',
      showCancelButton: true,
      confirmButtonText: 'Agregar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#667eea',
      cancelButtonColor: '#2d3746',
      inputValidator: (value: string) => {
        if (!value || value.trim().length === 0) {
          return 'El nombre es requerido';
        }
        if (value.trim().length < 3) {
          return 'El nombre debe tener al menos 3 caracteres';
        }
        return null;
      }
    });

    if (nombreEmpleado) {
      try {
        await EmpleadosService.addEmpleado(proyectoId, nombreEmpleado.trim());
        await Swal.fire({
          icon: 'success',
          title: 'Empleado agregado',
          text: 'La página se recargará',
          showConfirmButton: false,
          timer: 1500,
          background: '#0f1419',
          color: '#c8c8c8'
        });
        window.location.reload();
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo agregar el empleado',
          background: '#0f1419',
          color: '#c8c8c8'
        });
      }
    }
  },

  /**
   * Editar empleado
   */
  async editarEmpleado(empleadoId: number, nombreActual: string): Promise<void> {
    const { value: nuevoNombre } = await Swal.fire({
      title: 'Editar Empleado',
      input: 'text',
      inputLabel: 'Nombre del empleado',
      inputValue: nombreActual,
      showCancelButton: true,
      confirmButtonText: 'Guardar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#667eea',
      cancelButtonColor: '#2d3746',
      inputValidator: (value: string) => {
        if (!value || value.trim().length === 0) {
          return 'El nombre es requerido';
        }
        return null;
      }
    });

    if (nuevoNombre) {
      try {
        await EmpleadosService.updateEmpleado(empleadoId, nuevoNombre.trim());
        await Swal.fire({
          icon: 'success',
          title: 'Empleado actualizado',
          showConfirmButton: false,
          timer: 1500,
          background: '#0f1419',
          color: '#c8c8c8'
        });
        window.location.reload();
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo actualizar el empleado',
          background: '#0f1419',
          color: '#c8c8c8'
        });
      }
    }
  },

  /**
   * Eliminar empleado
   */
  async eliminarEmpleado(empleadoId: number, nombreEmpleado: string): Promise<void> {
    const result = await Swal.fire({
      title: '¿Eliminar empleado?',
      text: `Se eliminará a "${nombreEmpleado}" y todos sus registros`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#2d3746'
    });

    if (result.isConfirmed) {
      try {
        await EmpleadosService.deleteEmpleado(empleadoId);
        await Swal.fire({
          icon: 'success',
          title: 'Empleado eliminado',
          showConfirmButton: false,
          timer: 1500,
          background: '#0f1419',
          color: '#c8c8c8'
        });
        window.location.reload();
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo eliminar el empleado',
          background: '#0f1419',
          color: '#c8c8c8'
        });
      }
    }
  }
};
