/**
 * Service para Budget Addons
 * Fase 4: UX Unificada & Gestión Financiera
 */

import { apiFetch, API_ENDPOINTS } from '../utils/api';
import type {
  BudgetAddon,
  CreateBudgetAddonRequest,
  UpdateBudgetAddonRequest,
  BudgetAddonsResponse,
  TotalBudgetResponse
} from '../types/budgetAddon';

export const budgetAddonService = {
  /**
   * Obtiene todos los adicionales de un proyecto
   */
  async getProjectAddons(projectId: number): Promise<BudgetAddonsResponse> {
    return apiFetch<BudgetAddonsResponse>(API_ENDPOINTS.PROJECT_BUDGET_ADDONS(projectId));
  },

  /**
   * Crea un nuevo adicional de presupuesto
   */
  async create(projectId: number, data: CreateBudgetAddonRequest): Promise<{ addon: BudgetAddon; total_budget: number }> {
    return apiFetch<{ addon: BudgetAddon; total_budget: number }>(
      API_ENDPOINTS.PROJECT_BUDGET_ADDONS(projectId),
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Actualiza un adicional existente
   */
  async update(
    projectId: number,
    addonId: number,
    data: UpdateBudgetAddonRequest
  ): Promise<{ addon: BudgetAddon; total_budget: number }> {
    return apiFetch<{ addon: BudgetAddon; total_budget: number }>(
      API_ENDPOINTS.PROJECT_BUDGET_ADDON(projectId, addonId),
      {
        method: 'PUT',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Elimina un adicional
   */
  async delete(projectId: number, addonId: number): Promise<{ total_budget: number }> {
    return apiFetch<{ total_budget: number }>(
      API_ENDPOINTS.PROJECT_BUDGET_ADDON(projectId, addonId),
      { method: 'DELETE' }
    );
  },

  /**
   * Obtiene el presupuesto total (base + adicionales)
   */
  async getTotalBudget(projectId: number): Promise<TotalBudgetResponse> {
    return apiFetch<TotalBudgetResponse>(API_ENDPOINTS.PROJECT_TOTAL_BUDGET(projectId));
  },

  /**
   * Calcula el presupuesto total localmente
   */
  calculateTotal(baseAmount: number, addons: BudgetAddon[]): number {
    const addonsTotal = addons.reduce((sum, addon) => sum + addon.amount, 0);
    return baseAmount + addonsTotal;
  },

  /**
   * Formatea el monto según la moneda
   */
  formatAmount(amount: number, currency: string): string {
    const currencyMap: Record<string, string> = {
      'USD': '$',
      'EUR': '€',
      'ARS': '$',
      'MXN': '$',
      'CLP': '$',
      'COP': '$',
      'BRL': 'R$'
    };
    
    const symbol = currencyMap[currency] || currency;
    return `${symbol}${amount.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
};
