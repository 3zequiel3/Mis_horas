/**
 * Tipos para Multi-Tenant y Organizaciones
 */

export interface Organization {
  id: number;
  nombre: string;
  descripcion?: string;
  tipo_organizacion: 'empresa' | 'personal' | 'freelance';
  logo_url?: string;
  created_at: string;
  updated_at: string;
  owner_id: number;
  is_active: boolean;
  settings?: Record<string, any>;
}

export interface OrganizationMember {
  id: number;
  organization_id: number;
  user_id: number;
  role: 'owner' | 'admin' | 'manager' | 'member' | 'viewer';
  joined_at: string;
  invited_by?: number;
  is_active: boolean;
  user?: {
    id: number;
    nombre: string;
    email: string;
  };
}

export interface OrganizationInvitation {
  id: number;
  organization_id: number;
  email: string;
  role: 'admin' | 'manager' | 'member' | 'viewer';
  invited_by: number;
  created_at: string;
  expires_at: string;
  status: 'pending' | 'accepted' | 'rejected' | 'expired';
  organization?: Organization;
  inviter?: {
    id: number;
    nombre: string;
    email: string;
  };
}

export interface OrganizationStats {
  total_miembros: number;
  total_proyectos: number;
  proyectos_activos: number;
  plan?: string;
  limite_proyectos?: number | null;
  limite_miembros?: number | null;
}

export interface InviteMemberResponse {
  message: string;
  membership: OrganizationMember;
  es_nuevo_usuario: boolean;
}

export interface CreateOrganizationRequest {
  nombre: string;
  descripcion?: string;
  tipo_organizacion: 'empresa' | 'personal' | 'freelance';
  logo_url?: string;
}

export interface UpdateOrganizationRequest {
  nombre?: string;
  descripcion?: string;
  logo_url?: string;
  settings?: Record<string, any>;
}

export interface InviteMemberRequest {
  email: string;
  role: 'admin' | 'manager' | 'member' | 'viewer';
}

export interface UpdateMemberRoleRequest {
  role: 'admin' | 'manager' | 'member' | 'viewer';
}
