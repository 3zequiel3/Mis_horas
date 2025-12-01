/**
 * Servicio de API para Organizaciones
 */

import { apiFetch, API_ENDPOINTS } from '../utils/api';
import type {
  Organization,
  OrganizationMember,
  OrganizationInvitation,
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  InviteMemberRequest,
  UpdateMemberRoleRequest,
} from '../types/organization';

export const organizationService = {
  /**
   * Obtiene todas las organizaciones del usuario
   */
  async getAll(): Promise<Organization[]> {
    const result = await apiFetch<{ organizations: Organization[] }>(API_ENDPOINTS.ORGANIZACIONES);
    return result.organizations || [];
  },

  /**
   * Obtiene una organización por ID
   */
  async getById(id: number): Promise<Organization> {
    const result = await apiFetch<{ organization: Organization }>(API_ENDPOINTS.ORGANIZACION(id));
    if (!result.organization) {
      throw new Error('Organización no encontrada');
    }
    return result.organization;
  },

  /**
   * Crea una nueva organización
   */
  async create(data: CreateOrganizationRequest): Promise<Organization> {
    const result = await apiFetch<{ organization: Organization }>(
      API_ENDPOINTS.ORGANIZACIONES,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
    
    if (!result.organization) {
      throw new Error('Error al crear organización');
    }
    return result.organization;
  },

  /**
   * Actualiza una organización
   */
  async update(id: number, data: UpdateOrganizationRequest): Promise<Organization> {
    const result = await apiFetch<{ organization: Organization }>(
      API_ENDPOINTS.ORGANIZACION(id),
      {
        method: 'PUT',
        body: JSON.stringify(data),
      }
    );
    
    if (!result.organization) {
      throw new Error('Error al actualizar organización');
    }
    return result.organization;
  },

  /**
   * Elimina una organización
   */
  async delete(id: number): Promise<void> {
    await apiFetch(API_ENDPOINTS.ORGANIZACION(id), { method: 'DELETE' });
  },

  /**
   * Obtiene los miembros de una organización
   */
  async getMembers(organizationId: number): Promise<OrganizationMember[]> {
    const result = await apiFetch<{ members: OrganizationMember[] }>(
      API_ENDPOINTS.ORGANIZACION_MIEMBROS(organizationId)
    );
    return result.members || [];
  },

  /**
   * Invita a un nuevo miembro
   */
  async inviteMember(organizationId: number, data: InviteMemberRequest): Promise<OrganizationInvitation> {
    const result = await apiFetch<{ invitation: OrganizationInvitation }>(
      `${API_ENDPOINTS.ORGANIZACION(organizationId)}/invite`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
    
    if (!result.invitation) {
      throw new Error('Error al invitar miembro');
    }
    return result.invitation;
  },

  /**
   * Elimina un miembro de la organización
   */
  async removeMember(organizationId: number, userId: number): Promise<void> {
    await apiFetch(
      `${API_ENDPOINTS.ORGANIZACION_MIEMBROS(organizationId)}/${userId}`,
      { method: 'DELETE' }
    );
  },

  /**
   * Actualiza el rol de un miembro
   */
  async updateMemberRole(organizationId: number, userId: number, data: UpdateMemberRoleRequest): Promise<void> {
    await apiFetch(
      `${API_ENDPOINTS.ORGANIZACION_MIEMBROS(organizationId)}/${userId}/role`,
      {
        method: 'PUT',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Obtiene las invitaciones pendientes del usuario
   */
  async getMyInvitations(): Promise<OrganizationInvitation[]> {
    const result = await apiFetch<{ invitations: OrganizationInvitation[] }>(
      `${API_ENDPOINTS.ORGANIZACIONES}/invitations`
    );
    return result.invitations || [];
  },

  /**
   * Acepta una invitación
   */
  async acceptInvitation(invitationId: number): Promise<void> {
    await apiFetch(
      `${API_ENDPOINTS.ORGANIZACIONES}/invitations/${invitationId}/accept`,
      { method: 'POST' }
    );
  },

  /**
   * Rechaza una invitación
   */
  async rejectInvitation(invitationId: number): Promise<void> {
    await apiFetch(
      `${API_ENDPOINTS.ORGANIZACIONES}/invitations/${invitationId}/reject`,
      { method: 'POST' }
    );
  },

  /**
   * Cambia la organización actual
   */
  setCurrentOrganization(organizationId: number): void {
    localStorage.setItem('currentOrganizationId', organizationId.toString());
  },

  /**
   * Obtiene la organización actual
   */
  getCurrentOrganizationId(): number | null {
    const id = localStorage.getItem('currentOrganizationId');
    return id ? parseInt(id, 10) : null;
  },
};
