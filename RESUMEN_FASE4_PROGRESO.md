# 🎯 Resumen: Fase 4 - UX Unificada & Gestión Financiera (Progreso)

**Fecha:** 1 de diciembre de 2025  
**Estado:** ✅ Backend Completado | ✅ Componentes Visuales Completados | ⏳ Wizard y Drawer Pendientes

---

## 📊 Resumen Ejecutivo

Se está implementando la **Fase 4: UX Unificada & Gestión Financiera**, que transforma la experiencia de configuración de proyectos con:
- **Configuración modular** con toggles (Budget, Time Tracking, Audit, Public View)
- **Presupuestos flexibles** con adicionales sin tocar el base
- **Componentes visuales** para ver salud financiera de un vistazo
- **Branding personalizado** por proyecto

### Filosofía de Diseño
✅ **Consistencia estética** - Reutilizar componentes UI existentes  
✅ **Centralización** - Configuración dentro del proyecto (sin admin panels externos)  
✅ **Modularidad** - Funcionalidades activables/desactivables  

---

## ✅ Completado - Backend

### 1. Schema de Base de Datos ✅

**Extensión tabla `proyectos`** (6 nuevas columnas):
```sql
budget_type VARCHAR(30) DEFAULT 'none'
  - Valores: 'fixed_price', 'hourly_retainer', 'time_and_materials', 'none'
  
budget_base_amount DECIMAL(12,2) NULL
  - Monto base del presupuesto (dinero u horas según tipo)
  
currency VARCHAR(3) DEFAULT 'USD'
  - Código ISO: USD, EUR, ARS, MXN, BRL, etc.
  
modules_config JSON NULL
  - Estado de módulos: {"budget": true, "time_tracking": true, "audit": false, "public_view": false}
  
brand_color VARCHAR(7) NULL
  - Color hex para branding (#3B82F6)
  
client_name VARCHAR(255) NULL
  - Nombre del cliente asociado
```

**Nueva tabla `project_budget_addons`**:
```sql
CREATE TABLE project_budget_addons (
  id INT PRIMARY KEY,
  project_id INT,
  organization_id INT,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  amount DECIMAL(12,2) NOT NULL,
  created_by INT,
  created_at DATETIME,
  updated_at DATETIME
);
```

**Propósito:** Permitir ampliar presupuestos sin tocar el monto base
**Ejemplo:** Proyecto con $25,000 base + $5,000 "Fase 2 Extra" = $30,000 total

### 2. Vistas SQL Creadas ✅

**`v_project_total_budget`**:
```sql
- Calcula: budget_base + SUM(addons) = total_budget
- Agrupa por proyecto
- Incluye: addons_count, currency
```

**`v_project_burn_rate_enhanced`**:
```sql
- Integra adicionales en burn rate
- Calcula: (consumed / total_budget) * 100
- Health status: healthy/warning/critical/exceeded
- Remaining: total_budget - consumed
```

### 3. API Routes (5 endpoints) ✅

**`/api/projects/:projectId/budget-addons`**
```http
GET    /budget-addons              # Listar adicionales + totales
POST   /budget-addons              # Crear adicional
PUT    /budget-addons/:addonId     # Actualizar adicional
DELETE /budget-addons/:addonId     # Eliminar adicional
GET    /total-budget               # Obtener presupuesto total
```

**Permisos:**
- `VIEW_PROJECT_DETAILS` - Lectura
- `MANAGE_PROJECT_SETTINGS` - Escritura

**Response ejemplo:**
```json
{
  "addons": [
    {
      "id": 1,
      "name": "Fase 2 Extra",
      "amount": 5000.00,
      "description": "Funcionalidades adicionales"
    }
  ],
  "total_addons": 5000.00,
  "budget_base": 25000.00,
  "total_budget": 30000.00,
  "currency": "USD"
}
```

---

## ✅ Completado - Frontend

### 1. TypeScript Types ✅

**`budgetAddon.ts`**:
```typescript
interface BudgetAddon {
  id: number;
  project_id: number;
  name: string;
  description?: string;
  amount: number;
  created_at: string;
}

type BudgetType = 'none' | 'fixed_price' | 'hourly_retainer' | 'time_and_materials';

const BUDGET_TYPE_LABELS: Record<BudgetType, string> = {
  fixed_price: 'Monto fijo',
  hourly_retainer: 'Bolsa de horas',
  time_and_materials: 'Por hora (T&M)',
  none: 'Sin presupuesto'
};
```

**`projectConfig.ts`**:
```typescript
interface ModulesConfig {
  budget: boolean;
  time_tracking: boolean;
  audit: boolean;
  public_view: boolean;
}

interface ProjectConfig {
  budget_type: BudgetType;
  budget_base_amount?: number;
  currency: string;
  modules_config: ModulesConfig;
  brand_color?: string;
  client_name?: string;
}

type BudgetHealthStatus = 'healthy' | 'warning' | 'critical' | 'exceeded';

const CURRENCIES = [
  { code: 'USD', symbol: '$', name: 'Dólar estadounidense' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'ARS', symbol: '$', name: 'Peso argentino' },
  // ...
];
```

### 2. Services ✅

**`budgetAddonService.ts`**:
```typescript
budgetAddonService.getProjectAddons(projectId)
  → Promise<BudgetAddonsResponse>

budgetAddonService.create(projectId, data)
  → Promise<{ addon: BudgetAddon; total_budget: number }>

budgetAddonService.update(projectId, addonId, data)
  → Promise<{ addon: BudgetAddon; total_budget: number }>

budgetAddonService.delete(projectId, addonId)
  → Promise<{ total_budget: number }>

budgetAddonService.getTotalBudget(projectId)
  → Promise<TotalBudgetResponse>

// Helpers
budgetAddonService.calculateTotal(base, addons) → number
budgetAddonService.formatAmount(amount, currency) → string
```

### 3. Componentes Visuales ✅

#### **BurnBar.astro** ✅

Barra de progreso del burn rate con indicadores visuales:

**Props:**
```typescript
interface Props {
  burnRate: number;        // 0-100+
  consumed: number;        // Monto o horas consumidas
  total: number;          // Presupuesto total
  remaining: number;      // Restante (puede ser negativo)
  currency: string;
  budgetType: BudgetType;
}
```

**Lógica de colores:**
```typescript
< 50%:  Verde    (bg-green-500)   - Saludable
50-80%: Amarillo (bg-yellow-500)  - Advertencia
80-100%: Naranja (bg-orange-500)  - Crítico
> 100%:  Rojo    (bg-red-500)     - Excedido (con parpadeo)
```

**Features:**
- ✅ Animación de shimmer cuando excede 100%
- ✅ Badge de estado ("⚠ Cerca del límite", "✕ Presupuesto excedido")
- ✅ Muestra restante o excedido según el caso
- ✅ Soporta presupuestos monetarios y de horas

**Vista:**
```
┌─────────────────────────────────────────────────┐
│ Consumo del presupuesto  [⚠ Cerca del límite]  │ 75.0%
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░      │
│ Consumido: $18,750.00        Total: $25,000.00  │
│ Restante: $6,250.00                             │
└─────────────────────────────────────────────────┘
```

#### **ProfitabilityMeter.astro** ✅

Widget de rentabilidad con medidor semicircular:

**Props:**
```typescript
interface Props {
  profitMargin: number;    // Porcentaje de margen
  totalRevenue: number;    // Ingresos facturables
  totalCost: number;       // Costos totales
  netProfit: number;       // Ganancia neta
  currency: string;
  showDetails?: boolean;   // Mostrar detalles financieros
}
```

**Lógica de health status:**
```typescript
≥ 30%:  'healthy'  - Verde   (Excelente)
10-30%: 'warning'  - Amarillo (Aceptable)
0-10%:  'critical' - Naranja  (Bajo)
< 0%:   'losing'   - Rojo     (Pérdida)
```

**Features:**
- ✅ Medidor semicircular con arco de colores
- ✅ Aguja animada que indica el margen
- ✅ Porcentaje grande en el centro
- ✅ Detalles financieros: Ingresos, Costos, Ganancia Neta
- ✅ Badge de estado ("✓ Excelente", "⚠ Aceptable", etc.)
- ✅ Tooltip explicativo según estado

**Vista:**
```
┌───────────────────────────────────┐
│ Rentabilidad      [✓ Excelente]  │
│                                   │
│      ╱────────────────╲           │
│     ╱                  ╲          │
│    │      45.2%         │         │
│    │      Margen        │         │
│    ╲                   ╱          │
│     ╲─────────────────╱           │
│                                   │
│ Ingresos:  $50,000.00            │
│ Costos:    $27,400.00            │
│ ──────────────────────           │
│ Ganancia:  $22,600.00            │
└───────────────────────────────────┘
```

---

## ⏳ Pendiente - Frontend

### 1. Super Wizard Refactorización (Alta Prioridad)

Refactorizar el wizard de creación de proyectos a un **Stepper Dinámico**:

**Estructura:**

**Paso 1: Identidad del Proyecto**
```
- Nombre (requerido)
- Descripción (opcional)
- Cliente (dropdown si Empresa, input si Personal)
- Color de marca (color picker)
```

**Paso 2: Módulos Activables**
```
Toggles:
☑ Time Tracking (siempre activo por defecto)
☐ Presupuesto
☐ Auditoría
☐ Vista pública
```

**Paso 3: Estrategia Financiera (Condicional)**
*Solo si "Presupuesto" está activo en Paso 2*

3 Tarjetas seleccionables:

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  💰 Monto Fijo  │  │  ⏱ Bolsa Horas  │  │  💵 Por Hora   │
│                 │  │                 │  │     (T&M)       │
│ Input: $ USD    │  │ Input: Horas    │  │ Input: $/hora   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Paso 4: Equipo (Solo Empresa)**
```
Selector múltiple de empleados
Asignar roles rápidos (viewer, editor, admin)
```

**Lógica:**
- Si desactiva "Presupuesto" en Paso 2 → Paso 3 se oculta
- Si es Personal (no Empresa) → Paso 4 se oculta
- Navegación: Back, Next, Skip (cuando aplique)
- Progreso visual: "1 / 4", "2 / 4", etc.

### 2. ProjectSettingsDrawer (Alta Prioridad)

Drawer lateral (slide-over) que se abre desde el botón de engranaje ⚙️ en el tablero.

**Estructura:**

```
┌─────────────────────────────────────┐
│ ← Configuración del Proyecto     ✕ │
├─────────────────────────────────────┤
│ [General] [Módulos] [Finanzas] [Auditoría] │
├─────────────────────────────────────┤
│                                     │
│ TAB: GENERAL                        │
│ ├─ Editar nombre                    │
│ ├─ Editar descripción               │
│ ├─ Editar cliente                   │
│ ├─ Editar color de marca            │
│ └─ [Archivar proyecto]              │
│                                     │
│ TAB: MÓDULOS                        │
│ ├─ ☑ Time Tracking (locked)        │
│ ├─ ☐ Presupuesto                    │
│ ├─ ☐ Auditoría                      │
│ └─ ☐ Vista pública                  │
│                                     │
│ TAB: FINANZAS                       │
│ ├─ Presupuesto Base: $25,000       │
│ ├─ [+ Agregar Adicional]            │
│ ├─ Lista de adicionales:            │
│ │  ├─ Fase 2 Extra: $5,000 [✎] [✕] │
│ │  └─ Soporte Q1: $3,000 [✎] [✕]   │
│ └─ Total: $33,000                   │
│                                     │
│ TAB: AUDITORÍA                      │
│ └─ Timeline de acciones (readonly)  │
│                                     │
└─────────────────────────────────────┘
```

**Features requeridos:**
- Tabs para organizar configuración
- Formulario inline para editar adicionales
- Cálculo en tiempo real del total
- Confirmación antes de eliminar adicionales
- Integración con budgetAddonService

### 3. CSS Variables & Branding (Media Prioridad)

**Objetivos:**
1. Definir variables CSS en `:root` para colores
2. Configurar `tailwind.config.mjs` para usar variables
3. Lógica de branding:
   - **Personal:** Usa tema elegido por usuario (Dark/Light)
   - **Empresa:** Inyecta `brand_color` del proyecto en `--color-primary`

**Implementación:**

**`globals.css`:**
```css
:root {
  --color-primary: #3B82F6;  /* Default blue */
  --color-primary-dark: #2563EB;
  --color-primary-light: #60A5FA;
}

[data-project-color] {
  --color-primary: var(--project-brand-color);
  /* Calcular automáticamente dark/light variants */
}
```

**`tailwind.config.mjs`:**
```javascript
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          dark: 'var(--color-primary-dark)',
          light: 'var(--color-primary-light)',
        }
      }
    }
  }
}
```

**Lógica en layout:**
```typescript
// Si es empresa, inyectar brand_color
if (project.brand_color) {
  document.documentElement.style.setProperty('--project-brand-color', project.brand_color);
  document.documentElement.setAttribute('data-project-color', 'true');
}
```

---

## 🎨 Uso de los Componentes

### Integrar BurnBar en Dashboard del Proyecto

```astro
---
import BurnBar from '@/components/BurnBar.astro';
import { budgetService } from '@/services/budgetService';

// Obtener datos del presupuesto
const { budget_health } = await budgetService.getHealthStatus(projectId);
---

{project.modules_config.budget && (
  <div class="mb-6">
    <BurnBar
      burnRate={budget_health.burn_rate}
      consumed={budget_health.consumed_amount}
      total={budget_health.total_budget}
      remaining={budget_health.remaining}
      currency={project.currency}
      budgetType={project.budget_type}
    />
  </div>
)}
```

### Integrar ProfitabilityMeter en Dashboard

```astro
---
import ProfitabilityMeter from '@/components/ProfitabilityMeter.astro';
import { profitabilityService } from '@/services/profitabilityService';
import { hasPermission } from '@/utils/permissions';

// Solo mostrar si tiene permiso
const canViewFinancial = await hasPermission('VIEW_FINANCIAL_DATA');

// Obtener métricas
const profitability = await profitabilityService.getProjectProfitability(projectId);
---

{canViewFinancial && (
  <div class="col-span-1">
    <ProfitabilityMeter
      profitMargin={profitability.profit_margin}
      totalRevenue={profitability.billable_revenue}
      totalCost={profitability.internal_cost}
      netProfit={profitability.net_profit}
      currency={project.currency}
      showDetails={true}
    />
  </div>
)}
```

---

## 📐 Arquitectura de la Fase 4

### Flujo de Datos: Presupuesto con Adicionales

```
1. Usuario crea proyecto con presupuesto base $25,000
   ↓
2. Proyecto.budget_base_amount = 25000
   ↓
3. Usuario agrega "Fase 2 Extra" de $5,000
   ↓
4. POST /api/projects/1/budget-addons
   ↓
5. ProjectBudgetAddon.create({ amount: 5000 })
   ↓
6. Vista v_project_total_budget recalcula:
   total_budget = base (25000) + addons (5000) = 30000
   ↓
7. BurnBar muestra: consumed / 30000
   ↓
8. Budget.consumed_amount se actualiza con trigger
   ↓
9. BurnBar cambia de color según thresholds
```

### Flujo: Módulos Activables

```
1. Usuario activa módulo "Presupuesto" en Wizard Paso 2
   ↓
2. modules_config.budget = true
   ↓
3. Aparece Paso 3 (Estrategia Financiera)
   ↓
4. Usuario elige "Monto Fijo" e ingresa $25,000
   ↓
5. budget_type = 'fixed_price', budget_base_amount = 25000
   ↓
6. En Dashboard:
   if (project.modules_config.budget) {
     → Mostrar BurnBar
     → Mostrar ProfitabilityMeter
     → Mostrar tab "Finanzas" en Drawer
   }
```

---

## 🚀 Próximos Pasos

### Inmediato (Alta Prioridad)
1. **Refactorizar Wizard a Stepper** - Lógica condicional de pasos
2. **Crear ProjectSettingsDrawer** - Con tabs y CRUD de adicionales
3. **Implementar CSS Variables** - Para branding personalizado

### Medio Plazo
4. Integrar BurnBar y ProfitabilityMeter en dashboard real
5. Crear modal AddBudgetAddon para el drawer
6. Implementar permisos en drawer (quien puede editar configuración)

### Futuro
7. Exportar configuración de proyecto (JSON/PDF)
8. Templates de proyectos (guardar configuración para reutilizar)
9. Vista pública del proyecto (si modules_config.public_view = true)

---

## 📝 Archivos Creados en esta Sesión

### Backend
1. `/backend/app/models/proyecto.py` - Extendido con 6 nuevos campos
2. `/backend/app/models/project_budget_addon.py` - Modelo completo (70 líneas)
3. `/backend/migrations/add_fase4_ux_financial_config.sql` - Migration (313 líneas)
4. `/backend/app/routes/budget_addons.py` - API routes (5 endpoints, 210 líneas)

### Frontend
5. `/frontend/src/types/budgetAddon.ts` - Types y constantes (60 líneas)
6. `/frontend/src/types/projectConfig.ts` - Types de configuración (90 líneas)
7. `/frontend/src/services/budgetAddonService.ts` - Service completo (140 líneas)
8. `/frontend/src/components/BurnBar.astro` - Componente visual (150 líneas)
9. `/frontend/src/components/ProfitabilityMeter.astro` - Widget medidor (200 líneas)

**Total:** 9 archivos | ~1,230 líneas de código

---

## ✨ Highlights

### Lo que hace especial a Fase 4:

1. **Presupuestos Flexibles:** Agregar adicionales sin tocar el base es como tener "capas" de presupuesto
2. **Visualización Instantánea:** BurnBar y ProfitabilityMeter muestran salud financiera de un vistazo
3. **Modularidad Real:** Activar/desactivar funcionalidades cambia la interfaz dinámicamente
4. **Branding por Proyecto:** Cada proyecto puede tener su propio color (útil para agencias con múltiples clientes)

---

**Siguiente sesión:** Completar Wizard, Drawer y Branding System 🎨
