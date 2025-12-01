/**
 * Servicio de Organizaciones - API Client
 * Gestión de organizaciones y membresías (FASE 1 MULTI-TENANT)
 */

import type { Organization, OrganizationMember } from '../stores/organizationStore';
import { AuthService } from './auth';
import { ENV } from '../utils/env';

const API_URL = ENV.VITE_API_URL;

export interface CreateOrganizationDto {
  nombre: string;
  descripcion?: string;
  tipo_organizacion?: 'personal' | 'empresa' | 'freelance' | 'agencia';
  logo_url?: string;
}

export interface UpdateOrganizationDto {
  nombre?: string;
  descripcion?: string;
  logo_url?: string;
  zona_horaria?: string;
  moneda?: string;
}

export interface InviteMemberDto {
  email: string;
  role: 'admin' | 'manager' | 'member' | 'viewer';
}

export class OrganizationService {
  /**
   * Obtiene todas las organizaciones del usuario autenticado
   * Para el selector de contexto
   */
  static async getUserOrganizations(): Promise<Organization[]> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Error al obtener organizaciones');
    }

    return response.json();
  }

  /**
   * Obtiene detalles de una organización específica
   */
  static async getOrganization(orgId: number): Promise<Organization> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/${orgId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Error al obtener organización');
    }

    return response.json();
  }

  /**
   * Crea una nueva organización
   * El usuario se convierte en owner automáticamente
   */
  static async createOrganization(data: CreateOrganizationDto): Promise<Organization> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al crear organización');
    }

    const result = await response.json();
    return result.organization;
  }

  /**
   * Actualiza una organización
   */
  static async updateOrganization(orgId: number, data: UpdateOrganizationDto): Promise<Organization> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/${orgId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al actualizar organización');
    }

    const result = await response.json();
    return result.organization;
  }

  /**
   * Elimina una organización (solo owner)
   */
  static async deleteOrganization(orgId: number): Promise<void> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/${orgId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al eliminar organización');
    }
  }

  /**
   * Obtiene estadísticas de una organización
   */
  static async getOrganizationStats(orgId: number): Promise<any> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/${orgId}/stats`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Error al obtener estadísticas');
    }

    return response.json();
  }

  // ============================================================
  // GESTIÓN DE MIEMBROS
  // ============================================================

  /**
   * Obtiene todos los miembros de una organización
   */
  static async getOrganizationMembers(orgId: number): Promise<OrganizationMember[]> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/${orgId}/members`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Error al obtener miembros');
    }

    return response.json();
  }

  /**
   * Invita a un nuevo miembro por email
   */
  static async inviteMember(orgId: number, data: InviteMemberDto): Promise<any> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/${orgId}/members/invite`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al invitar miembro');
    }

    return response.json();
  }

  /**
   * Remueve un miembro de la organización
   */
  static async removeMember(orgId: number, userId: number): Promise<void> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/${orgId}/members/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al remover miembro');
    }
  }

  /**
   * Cambia el rol de un miembro
   */
  static async changeMemberRole(
    orgId: number,
    userId: number,
    role: 'admin' | 'manager' | 'member' | 'viewer'
  ): Promise<OrganizationMember> {
    const token = AuthService.getToken();
    if (!token) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/${orgId}/members/${userId}/role`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ role }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al cambiar rol');
    }

    const result = await response.json();
    return result.membership;
  }

  /**
   * Acepta una invitación a una organización
   */
  static async acceptInvitation(token: string): Promise<OrganizationMember> {
    const authToken = AuthService.getToken();
    if (!authToken) throw new Error('No autenticado');

    const response = await fetch(`${API_URL}/api/organizations/invitations/accept/${token}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al aceptar invitación');
    }

    const result = await response.json();
    return result.membership;
  }

  // ============================================================
  // HELPERS
  // ============================================================

  /**
   * Obtiene el header de organización para enviar con cada request
   */
  static getOrganizationHeader(orgId: number): Record<string, string> {
    return {
      'X-Organization-ID': orgId.toString(),
    };
  }
}
