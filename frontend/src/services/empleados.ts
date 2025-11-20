import { ApiService } from './api';
import type { Empleado } from '../types';

export class EmpleadosService extends ApiService {
  // Obtener empleados de un proyecto
  static async getEmpleadosByProyecto(proyectoId: number): Promise<Empleado[]> {
    return this.get(`/api/proyecto/${proyectoId}/empleados`);
  }

  // Alias para getEmpleadosByProyecto
  static async getEmpleados(proyectoId: number): Promise<Empleado[]> {
    return this.getEmpleadosByProyecto(proyectoId);
  }

  // Agregar empleado a un proyecto
  static async addEmpleado(proyectoId: number, nombre: string): Promise<Empleado> {
    return this.post(`/api/proyecto/${proyectoId}/empleados`, { nombre });
  }

  // Obtener un empleado específico
  static async getEmpleado(empleadoId: number): Promise<Empleado> {
    return this.get(`/api/empleados/${empleadoId}`);
  }

  // Actualizar empleado
  static async updateEmpleado(
    empleadoId: number,
    data: { nombre?: string; activo?: boolean }
  ): Promise<void> {
    await this.put(`/api/empleados/${empleadoId}`, data);
  }

  // Eliminar empleado
  static async deleteEmpleado(empleadoId: number): Promise<void> {
    await this.delete(`/api/empleados/${empleadoId}`);
  }
}
