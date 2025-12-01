/**
 * Inicializador de Contexto Organizacional
 * Se ejecuta en todas las páginas protegidas para asegurar que el contexto esté disponible
 * FASE 1 MULTI-TENANT
 */

import { initializeOrganizationStores, $organizations, $currentOrganization, setOrganizations, setCurrentOrganization } from '../stores/organizationStore';
import { OrganizationService } from '../services/organization';
import { AuthService } from '../services/auth';

let isInitialized = false;

export async function initializeOrganizationContext(): Promise<void> {
  // Evitar inicializar múltiples veces
  if (isInitialized) {
    return;
  }

  try {
    // Verificar que el usuario esté autenticado
    const token = AuthService.getToken();
    if (!token) {
      console.warn('No hay token de autenticación. Saltando inicialización de organizaciones.');
      return;
    }

    // Inicializar stores desde localStorage
    initializeOrganizationStores();

    // Verificar si ya hay organizaciones cargadas
    const currentOrgs = $organizations.get();
    const currentOrg = $currentOrganization.get();

    // Si ya hay datos en el store, no recargar
    if (currentOrgs.length > 0 && currentOrg) {
      isInitialized = true;
      return;
    }

    // Cargar organizaciones desde el servidor
    const organizations = await OrganizationService.getUserOrganizations();
    
    if (organizations.length === 0) {
      console.warn('El usuario no tiene organizaciones. Esto no debería ocurrir.');
      return;
    }

    // Guardar en store
    setOrganizations(organizations);

    // Si no hay organización actual, seleccionar la primera
    if (!currentOrg) {
      setCurrentOrganization(organizations[0]);
    }

    isInitialized = true;
    console.log('✅ Contexto organizacional inicializado:', organizations.length, 'organizaciones');
  } catch (error) {
    console.error('❌ Error al inicializar contexto organizacional:', error);
    // No bloquear la aplicación si falla
  }
}

/**
 * Hook para componentes que necesitan esperar a que el contexto esté listo
 */
export function waitForOrganizationContext(): Promise<void> {
  return new Promise((resolve) => {
    // Si ya está inicializado, resolver inmediatamente
    if (isInitialized) {
      resolve();
      return;
    }

    // Esperar a que se inicialice (máximo 5 segundos)
    let attempts = 0;
    const maxAttempts = 50;
    
    const interval = setInterval(() => {
      attempts++;
      
      if (isInitialized || attempts >= maxAttempts) {
        clearInterval(interval);
        resolve();
      }
    }, 100);
  });
}

/**
 * Verifica si hay un contexto organizacional válido
 */
export function hasOrganizationContext(): boolean {
  const org = $currentOrganization.get();
  return org !== null;
}

/**
 * Obtiene el ID de la organización actual o null
 */
export function getCurrentOrganizationId(): number | null {
  const org = $currentOrganization.get();
  return org?.id || null;
}
