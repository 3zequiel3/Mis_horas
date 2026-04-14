/**
 * Base API Service - Gestiona autenticación, headers y peticiones HTTP
 * Centraliza la lógica común para evitar repetición en todos los servicios
 * FASE 1 MULTI-TENANT: Incluye automáticamente el header X-Organization-ID
 */

import { getAuthHeaders } from '../utils/auth';
import { ENV } from '../utils/env';
import { $currentOrganizationId } from '../stores/organizationStore';

const API_URL = ENV.VITE_API_URL;

export class ApiService {
  /**
   * Obtiene los headers con autenticación y contexto organizacional
   * FASE 1 MULTI-TENANT: Agrega X-Organization-ID automáticamente
   */
  protected static getHeaders(): Record<string, string> {
    const headers = getAuthHeaders();
    
    // Agregar contexto organizacional si existe
    const orgId = $currentOrganizationId.get();
    if (orgId) {
      headers['X-Organization-ID'] = orgId.toString();
    }
    
    return headers;
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
      throw await this.handleError(response);
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
      throw await this.handleError(response);
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
      throw await this.handleError(response);
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
      throw await this.handleError(response);
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
      throw await this.handleError(response);
    }

    return response.json();
  }

  /**
   * Maneja errores de respuesta HTTP
   */
  private static async handleError(response: Response): Promise<Error> {
    const status = response.status;

    const errorMessages: Record<number, string> = {
      400: 'Solicitud inválida',
      401: 'No autenticado',
      403: 'No autorizado',
      404: 'Recurso no encontrado',
      422: 'Error de validación',
      500: 'Error del servidor',
    };

    let message = errorMessages[status] || `Error HTTP ${status}`;

    // Priorizar detalle de validación del backend (Pydantic/FastAPI style)
    if (status === 422) {
      try {
        const errorData = await response.clone().json();
        const detail = errorData?.detail;

        if (Array.isArray(detail) && detail.length > 0) {
          const first = detail[0];
          const field = Array.isArray(first?.loc) ? first.loc.join('.') : 'campo';
          const detailMessage = first?.msg || 'valor inválido';
          message = `${field}: ${detailMessage}`;
        } else if (typeof detail === 'string') {
          message = detail;
        }
      } catch {
        // Mantener mensaje base si no se puede parsear el body
      }
    }

    return new Error(message);
  }
}
