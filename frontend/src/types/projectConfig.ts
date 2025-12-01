/**
 * Types para Project Configuration
 * Fase 4: UX Unificada & Gestión Financiera
 */

import type { BudgetType } from './budgetAddon';

export interface ModulesConfig {
  budget: boolean;
  time_tracking: boolean;
  audit: boolean;
  approvals: boolean;
  public_view: boolean;
}

export interface ProjectConfig {
  id: number;
  nombre: string;
  descripcion?: string;
  client_name?: string;
  brand_color?: string;
  
  // Financial
  budget_type: BudgetType;
  budget_base_amount?: number;
  currency: string;
  
  // Modules
  modules_config: ModulesConfig;
  
  // Metadata
  organization_id: number;
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface UpdateProjectConfigRequest {
  nombre?: string;
  descripcion?: string;
  client_name?: string;
  brand_color?: string;
  budget_type?: BudgetType;
  budget_base_amount?: number;
  currency?: string;
  modules_config?: Partial<ModulesConfig>;
}

export interface ProjectFinancialSummary {
  budget_base: number;
  addons_total: number;
  total_budget: number;
  consumed_amount: number;
  consumed_hours: number;
  burn_rate: number;
  remaining: number;
  health_status: BudgetHealthStatus;
  currency: string;
}

export type BudgetHealthStatus = 'healthy' | 'warning' | 'critical' | 'exceeded';

export const HEALTH_STATUS_CONFIG: Record<BudgetHealthStatus, { label: string; color: string; icon: string }> = {
  healthy: {
    label: 'Saludable',
    color: 'text-green-600 bg-green-100',
    icon: '✓'
  },
  warning: {
    label: 'Advertencia',
    color: 'text-yellow-600 bg-yellow-100',
    icon: '⚠'
  },
  critical: {
    label: 'Crítico',
    color: 'text-orange-600 bg-orange-100',
    icon: '!'
  },
  exceeded: {
    label: 'Excedido',
    color: 'text-red-600 bg-red-100',
    icon: '✕'
  }
};

export const CURRENCIES: Array<{ code: string; symbol: string; name: string }> = [
  { code: 'USD', symbol: '$', name: 'Dólar estadounidense' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'ARS', symbol: '$', name: 'Peso argentino' },
  { code: 'MXN', symbol: '$', name: 'Peso mexicano' },
  { code: 'CLP', symbol: '$', name: 'Peso chileno' },
  { code: 'COP', symbol: '$', name: 'Peso colombiano' },
  { code: 'BRL', symbol: 'R$', name: 'Real brasileño' }
];
