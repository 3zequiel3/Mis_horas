/**
 * Store Global de Organizaciones (Nano Stores)
 * Gestiona el contexto organizacional actual del usuario
 * FASE 1 MULTI-TENANT
 */

import { atom, map, computed } from 'nanostores';

// ============================================================
// TIPOS
// ============================================================

export interface Organization {
  id: number;
  nombre: string;
  slug: string;
  descripcion?: string;
  logo_url?: string;
  zona_horaria: string;
  moneda: string;
  formato_fecha: string;
  owner_id: number;
  tipo_organizacion: 'personal' | 'empresa' | 'freelance' | 'agencia';
  plan_type: 'free' | 'starter' | 'professional' | 'enterprise';
  activa: boolean;
  fecha_creacion: string;
  estadisticas?: {
    total_miembros: number;
    total_proyectos: number;
    proyectos_activos: number;
    limite_proyectos?: number;
    limite_miembros?: number;
  };
}

export interface OrganizationMember {
  id: number;
  user_id: number;
  organization_id: number;
  role: 'owner' | 'admin' | 'manager' | 'member' | 'viewer';
  estado: 'activo' | 'suspendido' | 'invitado';
  fecha_ingreso: string;
  ultimo_acceso?: string;
  usuario?: {
    id: number;
    username: string;
    email: string;
    nombre_completo?: string;
    foto_perfil?: string;
  };
}

// ============================================================
// STORES
// ============================================================

/**
 * Lista de todas las organizaciones del usuario
 * Se carga al login
 */
export const $organizations = atom<Organization[]>([]);

/**
 * Organización actualmente seleccionada (contexto actual)
 * Persiste en localStorage
 */
export const $currentOrganization = atom<Organization | null>(null);

/**
 * Estado de carga
 */
export const $organizationsLoading = atom<boolean>(false);

/**
 * Membresía del usuario en la organización actual
 * Útil para verificar permisos
 */
export const $currentMembership = atom<OrganizationMember | null>(null);

// ============================================================
// COMPUTED STORES (Derivados)
// ============================================================

/**
 * ID de la organización actual (para headers de API)
 */
export const $currentOrganizationId = computed($currentOrganization, (org) => org?.id || null);

/**
 * Rol del usuario en la organización actual
 */
export const $currentRole = computed($currentMembership, (membership) => membership?.role || null);

/**
 * Verifica si el usuario es owner de la organización actual
 */
export const $isOwner = computed($currentRole, (role) => role === 'owner');

/**
 * Verifica si el usuario es admin o owner (permisos de gestión)
 */
export const $isAdminOrOwner = computed($currentRole, (role) => role === 'owner' || role === 'admin');

/**
 * Verifica si el usuario puede gestionar proyectos
 */
export const $canManageProjects = computed(
  $currentRole,
  (role) => role === 'owner' || role === 'admin' || role === 'manager'
);

// ============================================================
// PERSISTENCIA EN LOCALSTORAGE
// ============================================================

const LS_KEY_CURRENT_ORG = 'timeflow_current_organization';
const LS_KEY_ORGANIZATIONS = 'timeflow_organizations';

/**
 * Carga la organización desde localStorage
 */
export function loadOrganizationFromStorage(): Organization | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const stored = localStorage.getItem(LS_KEY_CURRENT_ORG);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Error al cargar organización desde localStorage:', error);
  }
  
  return null;
}

/**
 * Guarda la organización actual en localStorage
 */
export function saveOrganizationToStorage(org: Organization | null): void {
  if (typeof window === 'undefined') return;
  
  try {
    if (org) {
      localStorage.setItem(LS_KEY_CURRENT_ORG, JSON.stringify(org));
      // IMPORTANTE: También guardar el ID por separado para compatibilidad
      // con código legacy que busca directamente 'currentOrganizationId'
      localStorage.setItem('currentOrganizationId', org.id.toString());
    } else {
      localStorage.removeItem(LS_KEY_CURRENT_ORG);
      localStorage.removeItem('currentOrganizationId');
    }
  } catch (error) {
    console.error('Error al guardar organización en localStorage:', error);
  }
}

/**
 * Carga la lista de organizaciones desde localStorage (caché)
 */
export function loadOrganizationsFromStorage(): Organization[] {
  if (typeof window === 'undefined') return [];
  
  try {
    const stored = localStorage.getItem(LS_KEY_ORGANIZATIONS);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Error al cargar organizaciones desde localStorage:', error);
  }
  
  return [];
}

/**
 * Guarda la lista de organizaciones en localStorage (caché)
 */
export function saveOrganizationsToStorage(orgs: Organization[]): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.setItem(LS_KEY_ORGANIZATIONS, JSON.stringify(orgs));
  } catch (error) {
    console.error('Error al guardar organizaciones en localStorage:', error);
  }
}

// ============================================================
// ACCIONES
// ============================================================

/**
 * Establece la organización actual
 * Se persiste automáticamente
 */
export function setCurrentOrganization(org: Organization | null): void {
  $currentOrganization.set(org);
  saveOrganizationToStorage(org);
}

/**
 * Establece la lista de organizaciones
 * Se persiste automáticamente
 */
export function setOrganizations(orgs: Organization[]): void {
  $organizations.set(orgs);
  saveOrganizationsToStorage(orgs);
}

/**
 * Cambia a otra organización (switching)
 * Esto recargará toda la UI con el nuevo contexto
 */
export function switchOrganization(org: Organization): void {
  setCurrentOrganization(org);
  
  // Recargar la página para actualizar todos los datos con el nuevo contexto
  // En una app más avanzada, se podría hacer con eventos/observers
  if (typeof window !== 'undefined') {
    window.location.reload();
  }
}

/**
 * Inicializa los stores al cargar la app
 * Llamar una vez al inicio de la sesión
 */
export function initializeOrganizationStores(): void {
  // Cargar de localStorage
  const storedOrgs = loadOrganizationsFromStorage();
  const storedCurrentOrg = loadOrganizationFromStorage();
  
  if (storedOrgs.length > 0) {
    $organizations.set(storedOrgs);
  }
  
  if (storedCurrentOrg) {
    $currentOrganization.set(storedCurrentOrg);
    // Sincronizar también el ID en currentOrganizationId para compatibilidad
    if (typeof window !== 'undefined') {
      localStorage.setItem('currentOrganizationId', storedCurrentOrg.id.toString());
    }
  }
}

/**
 * Limpia todos los stores (logout)
 */
export function clearOrganizationStores(): void {
  $organizations.set([]);
  $currentOrganization.set(null);
  $currentMembership.set(null);
  $organizationsLoading.set(false);
  
  if (typeof window !== 'undefined') {
    localStorage.removeItem(LS_KEY_CURRENT_ORG);
    localStorage.removeItem(LS_KEY_ORGANIZATIONS);
    localStorage.removeItem('currentOrganizationId');
  }
}

// ============================================================
// HELPERS DE PERMISOS
// ============================================================

/**
 * Verifica si el usuario actual tiene un permiso específico
 */
export function hasPermission(permission: string): boolean {
  const membership = $currentMembership.get();
  if (!membership) return false;
  
  const permissions: Record<string, string[]> = {
    owner: [
      'view_all', 'edit_all', 'delete_all',
      'manage_organization', 'manage_billing', 'manage_members',
      'manage_projects', 'view_finance', 'edit_finance',
      'approve_hours', 'view_team_hours',
    ],
    admin: [
      'view_all', 'edit_all',
      'manage_members', 'manage_projects',
      'view_finance', 'edit_finance',
      'approve_hours', 'view_team_hours',
    ],
    manager: [
      'view_all', 'edit_projects',
      'approve_hours', 'view_team_hours',
    ],
    member: [
      'view_own', 'edit_own',
    ],
    viewer: [
      'view_all',
    ],
  };
  
  const rolePermissions = permissions[membership.role] || [];
  return rolePermissions.includes(permission);
}
