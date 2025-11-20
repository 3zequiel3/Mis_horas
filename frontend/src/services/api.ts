/**
 * Base API Service - Gestiona autenticación, headers y peticiones HTTP
 * Centraliza la lógica común para evitar repetición en todos los servicios
 */

import { getAuthHeaders } from '../utils/auth';
import { ENV } from '../utils/env';

const API_URL = ENV.VITE_API_URL;

export class ApiService {
  /**
   * Obtiene los headers con autenticación
   */
  protected static getHeaders(): Record<string, string> {
    return getAuthHeaders();
  }

  /**
   * Realiza una petición GET
   */
  protected static async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: this.getHeaders(),
      credentials: 'include',
    });

    if (!response.ok) {
      throw this.handleError(response);
    }

    return response.json();
  }

  /**
   * Realiza una petición POST
   */
  protected static async post<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        ...this.getHeaders(),
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      throw this.handleError(response);
    }

    return response.json();
  }

  /**
   * Realiza una petición PUT
   */
  protected static async put<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        ...this.getHeaders(),
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      throw this.handleError(response);
    }

    return response.json();
  }

  /**
   * Realiza una petición PATCH
   */
  protected static async patch<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'PATCH',
      headers: {
        ...this.getHeaders(),
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      throw this.handleError(response);
    }

    return response.json();
  }

  /**
   * Realiza una petición DELETE
   */
  protected static async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
      credentials: 'include',
    });

    if (!response.ok) {
      throw this.handleError(response);
    }

    return response.json();
  }

  /**
   * Maneja errores de respuesta HTTP
   */
  private static handleError(response: Response): Error {
    const status = response.status;

    const errorMessages: Record<number, string> = {
      400: 'Solicitud inválida',
      401: 'No autenticado',
      403: 'No autorizado',
      404: 'Recurso no encontrado',
      500: 'Error del servidor',
    };

    const message = errorMessages[status] || `Error HTTP ${status}`;
    return new Error(message);
  }
}
