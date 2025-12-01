/**
 * Utilidades para detectar y manejar Modo Personal/Freelance
 * Simplifica la UI automáticamente cuando el usuario trabaja solo
 */

import { organizationService } from '../services/organizationService';
import type { Organization } from '../types/organization';

/**
 * Verifica si la organización actual es de tipo personal/freelance
 */
export async function isCurrentOrgPersonal(): Promise<boolean> {
  try {
    const orgId = organizationService.getCurrentOrganizationId();
    if (!orgId) return false;

    const organizations = await organizationService.getAll();
    const currentOrg = organizations.find(o => o.id === orgId);
    
    return currentOrg ? ['personal', 'freelance'].includes(currentOrg.tipo_organizacion) : false;
  } catch (error) {
    console.error('Error verificando tipo de organización:', error);
    return false;
  }
}

/**
 * Verifica si debe mostrarse el sistema de aprobaciones
 * En modo personal/freelance se auto-aprueban las entradas
 */
export async function shouldShowApprovals(): Promise<boolean> {
  const isPersonal = await isCurrentOrgPersonal();
  return !isPersonal;
}

/**
 * Verifica si debe mostrarse el sistema de auditoría completo
 * En modo personal se simplifica
 */
export async function shouldShowFullAudit(): Promise<boolean> {
  const isPersonal = await isCurrentOrgPersonal();
  return !isPersonal;
}

/**
 * Verifica si debe mostrarse la gestión de miembros
 * En modo personal no tiene sentido invitar a otros
 */
export async function shouldShowMemberManagement(): Promise<boolean> {
  const isPersonal = await isCurrentOrgPersonal();
  return !isPersonal;
}

/**
 * Auto-aprueba una entrada de tiempo si está en modo personal
 */
export async function autoApproveIfPersonal(timeEntryId: number): Promise<void> {
  const isPersonal = await isCurrentOrgPersonal();
  
  if (isPersonal) {
    // En modo personal, marcar como aprobado automáticamente
    // El backend debe manejar esto también
    console.log('Modo personal: auto-aprobando entrada de tiempo', timeEntryId);
    // Aquí se haría la llamada al backend si fuera necesario
  }
}

/**
 * Obtiene un mensaje personalizado según el modo
 */
export async function getWelcomeMessage(): Promise<string> {
  const isPersonal = await isCurrentOrgPersonal();
  
  if (isPersonal) {
    return '¡Hola! Gestiona tu tiempo de forma simple y efectiva.';
  } else {
    return '¡Bienvenido! Gestiona tu equipo y proyectos empresariales.';
  }
}

/**
 * Ajusta la visibilidad de elementos de la UI según el modo
 */
export function adjustUIForPersonalMode() {
  // Esta función debe ser llamada después de que el DOM esté listo
  isCurrentOrgPersonal().then(isPersonal => {
    if (isPersonal) {
      // Ocultar elementos innecesarios en modo personal
      const elementsToHide = [
        '#nav-aprobaciones',    // Link de aprobaciones en header
        '.member-management',   // Secciones de gestión de miembros
        '.role-badges',         // Badges de roles
        '.approval-workflow',   // Widgets de workflow de aprobación
      ];

      elementsToHide.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) {
          (element as HTMLElement).style.display = 'none';
        }
      });

      // Simplificar mensajes
      const createProjectBtn = document.querySelector('[href="/nuevo-proyecto"]');
      if (createProjectBtn) {
        createProjectBtn.textContent = '+ Nuevo Proyecto';
      }
    }
  });
}

/**
 * Estado por defecto para nuevas entradas de tiempo en modo personal
 */
export async function getDefaultTimeEntryStatus(): Promise<'draft' | 'pending' | 'approved'> {
  const isPersonal = await isCurrentOrgPersonal();
  return isPersonal ? 'approved' : 'draft';
}

/**
 * Verifica si el usuario debe ver precios/costos
 * En modo personal siempre ve sus propios números
 */
export async function canViewFinancialData(): Promise<boolean> {
  const isPersonal = await isCurrentOrgPersonal();
  if (isPersonal) return true;

  // En modo empresarial depende del rol
  const userStr = localStorage.getItem('user');
  if (!userStr) return false;

  try {
    const user = JSON.parse(userStr);
    return ['owner', 'admin'].includes(user.role);
  } catch {
    return false;
  }
}
