/**
 * Servicio de Organizaciones - API Client
 * Gestión de organizaciones y membresías (FASE 1 MULTI-TENANT)
 */

import type { Organization, OrganizationMember } from '../stores/organizationStore';
import { apiFetch } from '../utils/api';

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

export interface OrganizationStats {
  total_miembros: number;
  total_proyectos: number;
  proyectos_activos: number;
  plan?: string;
  limite_proyectos?: number | null;
  limite_miembros?: number | null;
}

interface CreateOrganizationResponse {
  message: string;
  organization: Organization;
}

interface UpdateOrganizationResponse {
  message: string;
  organization: Organization;
}

interface InviteMemberResponse {
  message: string;
  membership: OrganizationMember;
  es_nuevo_usuario: boolean;
}

interface ChangeRoleResponse {
  message: string;
  membership: OrganizationMember;
}

interface AcceptInvitationResponse {
  message: string;
  membership: OrganizationMember;
}

export class OrganizationService {
  /**
   * Obtiene todas las organizaciones del usuario autenticado
   * Para el selector de contexto
   */
  static async getUserOrganizations(): Promise<Organization[]> {
    return apiFetch<Organization[]>('/api/organizations');
  }

  /**
   * Obtiene detalles de una organización específica
   */
  static async getOrganization(orgId: number): Promise<Organization> {
    return apiFetch<Organization>(`/api/organizations/${orgId}`);
  }

  /**
   * Crea una nueva organización
   * El usuario se convierte en owner automáticamente
   */
  static async createOrganization(data: CreateOrganizationDto): Promise<Organization> {
    const result = await apiFetch<CreateOrganizationResponse>('/api/organizations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return result.organization;
  }

  /**
   * Actualiza una organización
   */
  static async updateOrganization(orgId: number, data: UpdateOrganizationDto): Promise<Organization> {
    const result = await apiFetch<UpdateOrganizationResponse>(`/api/organizations/${orgId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return result.organization;
  }

  /**
   * Elimina una organización (solo owner)
   */
  static async deleteOrganization(orgId: number): Promise<void> {
    await apiFetch<{ message: string }>(`/api/organizations/${orgId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Obtiene estadísticas de una organización
   */
  static async getOrganizationStats(orgId: number): Promise<OrganizationStats> {
    return apiFetch<OrganizationStats>(`/api/organizations/${orgId}/stats`);
  }

  // ============================================================
  // GESTIÓN DE MIEMBROS
  // ============================================================

  /**
   * Obtiene todos los miembros de una organización
   */
  static async getOrganizationMembers(orgId: number): Promise<OrganizationMember[]> {
    return apiFetch<OrganizationMember[]>(`/api/organizations/${orgId}/members`);
  }

  /**
   * Invita a un nuevo miembro por email
   */
  static async inviteMember(
    orgId: number,
    dataOrEmail: InviteMemberDto | string,
    role?: 'admin' | 'manager' | 'member' | 'viewer'
  ): Promise<InviteMemberResponse> {
    const payload: InviteMemberDto =
      typeof dataOrEmail === 'string'
        ? { email: dataOrEmail, role: role || 'member' }
        : dataOrEmail;

    return apiFetch<InviteMemberResponse>(`/api/organizations/${orgId}/members/invite`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Remueve un miembro de la organización
   */
  static async removeMember(orgId: number, userId: number): Promise<void> {
    await apiFetch<{ message: string }>(`/api/organizations/${orgId}/members/${userId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Cambia el rol de un miembro
   */
  static async changeMemberRole(
    orgId: number,
    userId: number,
    role: 'admin' | 'manager' | 'member' | 'viewer'
  ): Promise<OrganizationMember> {
    const result = await apiFetch<ChangeRoleResponse>(`/api/organizations/${orgId}/members/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    });
    return result.membership;
  }

  /**
   * Alias de compatibilidad con vistas existentes
   */
  static async updateMemberRole(
    orgId: number,
    userId: number,
    role: 'admin' | 'manager' | 'member' | 'viewer'
  ): Promise<OrganizationMember> {
    return this.changeMemberRole(orgId, userId, role);
  }

  /**
   * Acepta una invitación a una organización
   */
  static async acceptInvitation(token: string): Promise<OrganizationMember> {
    const result = await apiFetch<AcceptInvitationResponse>(`/api/organizations/invitations/accept/${token}`, {
      method: 'POST',
    });
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
