/**
 * Utilidades para verificar permisos en el frontend
 */

import { Permission, ROLE_PERMISSIONS, type Role } from '../types/approval';
import type { Organization } from '../types/organization';

/**
 * Verifica si un rol tiene un permiso específico
 */
export function hasPermission(role: Role, permission: Permission): boolean {
  const permissions = ROLE_PERMISSIONS[role];
  return permissions.includes(permission);
}

/**
 * Verifica si un rol tiene alguno de los permisos especificados
 */
export function hasAnyPermission(role: Role, permissions: Permission[]): boolean {
  return permissions.some(permission => hasPermission(role, permission));
}

/**
 * Verifica si un rol tiene todos los permisos especificados
 */
export function hasAllPermissions(role: Role, permissions: Permission[]): boolean {
  return permissions.every(permission => hasPermission(role, permission));
}

/**
 * Verifica si un usuario puede acceder a datos financieros
 */
export function canAccessFinancialData(role: Role): boolean {
  return hasPermission(role, Permission.VIEW_FINANCIAL_DATA);
}

/**
 * Verifica si un usuario puede ver tasas horarias
 */
export function canViewHourlyRates(role: Role): boolean {
  return hasPermission(role, Permission.VIEW_HOURLY_RATES);
}

/**
 * Verifica si un usuario puede aprobar hojas de tiempo
 */
export function canApproveTimesheets(role: Role): boolean {
  return hasPermission(role, Permission.APPROVE_TIMESHEETS);
}

/**
 * Verifica si un usuario puede gestionar la organización
 */
export function canManageOrganization(role: Role): boolean {
  return hasPermission(role, Permission.MANAGE_ORGANIZATION);
}

/**
 * Verifica si un usuario puede invitar miembros
 */
export function canInviteMembers(role: Role): boolean {
  return hasPermission(role, Permission.INVITE_MEMBERS);
}

/**
 * Verifica si un usuario puede eliminar miembros
 */
export function canRemoveMembers(role: Role): boolean {
  return hasPermission(role, Permission.REMOVE_MEMBERS);
}

/**
 * Verifica si un usuario puede cambiar roles de miembros
 */
export function canChangeMemberRoles(role: Role): boolean {
  return hasPermission(role, Permission.CHANGE_MEMBER_ROLES);
}

/**
 * Verifica si una organización está en modo personal
 */
export function isPersonalMode(organization: Organization): boolean {
  return ['personal', 'freelance'].includes(organization.tipo_organizacion);
}

/**
 * Verifica si se debe mostrar el sistema de aprobaciones
 */
export function shouldShowApprovalSystem(organization: Organization): boolean {
  // En modo personal/freelance no se muestra el sistema de aprobaciones
  return !isPersonalMode(organization);
}

/**
 * Verifica si se debe auto-aprobar las entradas de tiempo
 */
export function shouldAutoApprove(organization: Organization): boolean {
  // En modo personal/freelance las entradas se auto-aprueban
  return isPersonalMode(organization);
}

/**
 * Obtiene el texto descriptivo de un rol
 */
export function getRoleLabel(role: Role): string {
  const labels: Record<Role, string> = {
    owner: 'Propietario',
    admin: 'Administrador',
    manager: 'Gerente',
    member: 'Miembro',
    viewer: 'Observador',
  };
  return labels[role] || role;
}

/**
 * Obtiene el color asociado a un rol
 */
export function getRoleColor(role: Role): string {
  const colors: Record<Role, string> = {
    owner: 'bg-purple-100 text-purple-800 border-purple-300',
    admin: 'bg-red-100 text-red-800 border-red-300',
    manager: 'bg-blue-100 text-blue-800 border-blue-300',
    member: 'bg-green-100 text-green-800 border-green-300',
    viewer: 'bg-gray-100 text-gray-800 border-gray-300',
  };
  return colors[role] || 'bg-gray-100 text-gray-800 border-gray-300';
}

/**
 * Obtiene la descripción de un rol
 */
export function getRoleDescription(role: Role): string {
  const descriptions: Record<Role, string> = {
    owner: 'Control total sobre la organización y todos sus recursos',
    admin: 'Gestión completa de proyectos, empleados y configuración',
    manager: 'Aprobación de tiempo y gestión de proyectos asignados',
    member: 'Registro de tiempo y tareas asignadas',
    viewer: 'Solo lectura de información',
  };
  return descriptions[role] || '';
}

/**
 * Filtra una lista de permisos para mostrar solo los disponibles para un rol
 */
export function getAvailablePermissions(role: Role): Permission[] {
  return ROLE_PERMISSIONS[role];
}

/**
 * Verifica si el usuario actual puede realizar una acción sobre otro usuario
 */
export function canManageUser(currentUserRole: Role, targetUserRole: Role): boolean {
  const roleHierarchy: Record<Role, number> = {
    owner: 5,
    admin: 4,
    manager: 3,
    member: 2,
    viewer: 1,
  };

  return roleHierarchy[currentUserRole] > roleHierarchy[targetUserRole];
}

/**
 * Obtiene el rol del usuario actual desde el localStorage
 */
export function getCurrentUserRole(): Role | null {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;

  try {
    const user = JSON.parse(userStr);
    return user.role || null;
  } catch {
    return null;
  }
}

/**
 * Verifica si el usuario actual tiene un permiso
 */
export function currentUserHasPermission(permission: Permission): boolean {
  const role = getCurrentUserRole();
  if (!role) return false;
  return hasPermission(role, permission);
}
