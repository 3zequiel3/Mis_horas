import type { Dia, CreateDiaRequest, UpdateDiaRequest } from '../types';
import { getAuthHeaders } from '../utils/auth';
import { ENV } from '../utils/env';

const API_URL = ENV.VITE_API_URL;

export class DiasService {
  /**
   * Obtiene todos los días de un proyecto en un mes específico
   */
  static async getDiasPorProyecto(proyectoId: number, anio?: number, mes?: number): Promise<Dia[]> {
    
    
    let url = `${API_URL}/api/dias?proyecto_id=${proyectoId}`;
    if (anio !== undefined) url += `&anio=${anio}`;
    if (mes !== undefined) url += `&mes=${mes}`;
    
    const response = await fetch(url, {
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) {
      throw new Error('Error al obtener días');
    }

    return response.json();
  }

  /**
   * Obtiene un día específico
   */
  static async getDia(diaId: number): Promise<Dia> {
    
    
    const response = await fetch(`${API_URL}/api/dias/${diaId}`, {
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) {
      throw new Error('Día no encontrado');
    }

    return response.json();
  }

  /**
   * Crea un nuevo día de trabajo
   */
  static async createDia(data: CreateDiaRequest): Promise<Dia> {
    
    
    const response = await fetch(`${API_URL}/api/dias`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al crear día');
    }

    return response.json();
  }

  /**
   * Actualiza las horas de un día
   */
  static async updateDia(diaId: number, data: UpdateDiaRequest): Promise<Dia> {
    
    
    const response = await fetch(`${API_URL}/api/dias/${diaId}`, {
      method: 'PUT',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al actualizar día');
    }

    return response.json();
  }

  /**
   * Elimina un día
   */
  static async deleteDia(diaId: number): Promise<void> {
    
    
    const response = await fetch(`${API_URL}/api/dias/${diaId}`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al eliminar día');
    }
  }

  /**
   * Obtiene resumen de horas de un período
   */
  static async getResumenHoras(proyectoId: number, anio: number, mes: number): Promise<{
    total_horas: number;
    horas_reales: number;
    dias_trabajados: number;
  }> {
    
    
    const response = await fetch(
      `${API_URL}/api/dias/resumen?proyecto_id=${proyectoId}&anio=${anio}&mes=${mes}`,
      {
        headers: {
          ...getAuthHeaders(),
        },
      }
    );

    if (!response.ok) {
      throw new Error('Error al obtener resumen de horas');
    }

    return response.json();
  }
}
