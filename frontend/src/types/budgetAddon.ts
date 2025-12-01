/**
 * Types para Budget Addons
 * Fase 4: UX Unificada & Gestión Financiera
 */

export interface BudgetAddon {
  id: number;
  project_id: number;
  organization_id: number;
  name: string;
  description?: string;
  amount: number;
  created_by?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateBudgetAddonRequest {
  name: string;
  description?: string;
  amount: number;
}

export interface UpdateBudgetAddonRequest {
  name?: string;
  description?: string;
  amount?: number;
}

export interface BudgetAddonsResponse {
  addons: BudgetAddon[];
  total_addons: number;
  budget_base: number;
  total_budget: number;
  currency: string;
}

export interface TotalBudgetResponse {
  budget_type: BudgetType;
  budget_base: number;
  addons_total: number;
  total_budget: number;
  currency: string;
}

export type BudgetType = 'none' | 'fixed_price' | 'hourly_retainer' | 'time_and_materials';

export const BUDGET_TYPE_LABELS: Record<BudgetType, string> = {
  none: 'Sin presupuesto',
  fixed_price: 'Monto fijo',
  hourly_retainer: 'Bolsa de horas',
  time_and_materials: 'Por hora (T&M)'
};

export const BUDGET_TYPE_DESCRIPTIONS: Record<BudgetType, string> = {
  none: 'El proyecto no tiene presupuesto definido',
  fixed_price: 'Precio fijo acordado con el cliente',
  hourly_retainer: 'Cantidad de horas disponibles',
  time_and_materials: 'Se cobra por tiempo y materiales'
};
