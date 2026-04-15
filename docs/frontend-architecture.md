# TimeFlow — Arquitectura Frontend

## Stack

| Tecnología | Versión | Rol |
|-----------|---------|-----|
| **Astro** | 6.1.3 | Framework SSR, file-based routing, middleware |
| **Alpine.js** | 3.15+ | Interactividad declarativa en HTML |
| **Tailwind CSS** | 4.2 | Utilidades CSS, `@theme` nativo |
| **Nanostores** | 1.2 | Estado global (organizationStore) |
| **TypeScript** | 6.0 | Tipado en handlers, services, utils, types |
| **SweetAlert2** | 11.x | Modales de confirmación y alertas |
| **jsPDF + html2canvas** | — | Exportación a PDF client-side |

---

## ¿Por qué NO React?

React fue integrado en una iteración anterior como `@astrojs/react` con componentes `.tsx`. Se **eliminó por completo** en la Fase 5 por estas razones:

1. **No se usaba**: Ningún componente React estaba activo en producción. Alpine.js ya manejaba toda la interactividad.
2. **Bloat innecesario**: React + ReactDOM agregan ~40KB gzipped al bundle sin aportar valor.
3. **Complejidad de hidratación**: Los islands de Astro con React requieren `client:*` directives y manejan estado de forma diferente a Alpine.js — dos paradigmas en conflicto.
4. **Alpine.js es suficiente**: Para formularios, modales, dropdowns, toggles y fetch de API, Alpine.js con `x-data` resuelve todo sin overhead.

**Qué se eliminó:**
- `@astrojs/react`, `react`, `react-dom` de dependencias
- Archivos `.tsx` huérfanos
- Configuración de React en `astro.config.mjs`

---

## Sistema de Design Tokens

La arquitectura de estilos sigue un flujo de 3 capas:

```
tokens.css (fuente de verdad)
    ↓
global.css (@theme mapea tokens → Tailwind utilities)
    ↓
[feature].css (@layer components con estilos específicos)
```

### 1. `tokens.css` — Declaración

Define TODAS las variables del sistema bajo el namespace `--tf-*`:

```css
:root {
  --tf-color-primary: #667eea;
  --tf-bg-surface: #1a1a2e;
  --tf-text-primary: #f1f5f9;
  --tf-radius-md: 8px;
  /* ... */
}
```

### 2. `global.css` — Bridge a Tailwind

Mapea tokens a variables de Tailwind 4 para usar como utilidades:

```css
@import "tailwindcss";

@theme {
  --color-primary: var(--tf-color-primary);
  --color-surface: var(--tf-bg-surface);
  --radius-md: var(--tf-radius-md);
}
```

Esto permite usar `bg-primary`, `text-surface`, `rounded-md` directamente en HTML.

### 3. `[feature].css` — Componentes

Cada feature tiene su CSS con `@layer components`:

```css
@layer components {
  .task-row { /* ... */ }
  .task-row:hover { /* ... */ }
}
```

> **Referencia completa de tokens**: Ver [design-tokens.md](design-tokens.md).

---

## Referencia Completa de Tokens en @theme

| Variable @theme | Token fuente | Utility class generada |
|----------------|-------------|----------------------|
| `--color-primary` | `--tf-color-primary` | `bg-primary`, `text-primary`, `border-primary` |
| `--color-primary-hover` | `--tf-color-primary-hover` | `bg-primary-hover` |
| `--color-accent` | `--tf-color-accent` | `bg-accent`, `text-accent` |
| `--color-accent-hover` | `--tf-color-accent-hover` | `bg-accent-hover` |
| `--color-success` | `--tf-color-success` | `bg-success`, `text-success` |
| `--color-danger` | `--tf-color-danger` | `bg-danger`, `text-danger` |
| `--color-warning` | `--tf-color-warning` | `bg-warning`, `text-warning` |
| `--color-info` | `--tf-color-info` | `bg-info`, `text-info` |
| `--color-surface` | `--tf-bg-surface` | `bg-surface` |
| `--color-elevated` | `--tf-bg-elevated` | `bg-elevated` |
| `--color-base` | `--tf-bg-base` | `bg-base` |
| `--color-tf-text` | `--tf-text-primary` | `text-tf-text` |
| `--color-tf-text-secondary` | `--tf-text-secondary` | `text-tf-text-secondary` |
| `--color-tf-text-muted` | `--tf-text-muted` | `text-tf-text-muted` |
| `--color-tf-border` | `--tf-border` | `border-tf-border` |
| `--radius-sm` | `--tf-radius-sm` | `rounded-sm` |
| `--radius-md` | `--tf-radius-md` | `rounded-md` |
| `--radius-lg` | `--tf-radius-lg` | `rounded-lg` |
| `--radius-xl` | `--tf-radius-xl` | `rounded-xl` |

---

## Inventario de Componentes

15 componentes `.astro` en `src/components/`:

| Componente | Descripción |
|-----------|-------------|
| `Header.astro` | Navegación principal, selector de organización, menú usuario |
| `ProjectSidebar.astro` | Sidebar izquierdo en vista de proyecto — navegación por meses |
| `ConfigDrawer.astro` | Drawer lateral derecho — configuración general |
| `ProjectSettingsDrawer.astro` | Drawer lateral derecho — settings de proyecto (rates, budget) |
| `SuperWizard.astro` | Wizard multi-step de onboarding/configuración |
| `InvitacionesModal.astro` | Modal para gestionar invitaciones a proyecto |
| `TurnosModal.astro` | Modal para gestionar turnos de trabajo |
| `Notificaciones.astro` | Panel de notificaciones in-app |
| `OrganizationSelector.astro` | Dropdown de selección de organización activa |
| `ProtectedRoute.astro` | Wrapper de protección de ruta (verifica auth) |
| `TimeInput.astro` | Input especializado para ingreso de horas (HH:MM) |
| `BurnBar.astro` | Barra de progreso de consumo de presupuesto |
| `ProfitabilityMeter.astro` | Indicador visual de margen de rentabilidad |
| `ApprovalHistoryTimeline.astro` | Timeline vertical de historial de aprobaciones |
| `PDFTemplate.astro` | Template para exportación a PDF |

---

## Mapa de Páginas

### Rutas Principales

| Ruta | Archivo | Descripción |
|------|---------|-------------|
| `/` | `index.astro` | Landing / redirect a login o dashboard |
| `/login` | `login.astro` | Login con JWT |
| `/register` | `register.astro` | Registro de usuario |
| `/dashboard` | `dashboard.astro` | Dashboard principal con métricas |
| `/perfil` | `perfil.astro` | Perfil de usuario |
| `/proyectos` | `proyectos.astro` | Lista de proyectos |
| `/nuevo-proyecto` | `nuevo-proyecto.astro` | Crear proyecto |
| `/invitations` | `invitations.astro` | Invitaciones pendientes |

### Rutas Dinámicas

| Ruta | Archivo | Descripción |
|------|---------|-------------|
| `/proyecto/[id]` | `proyecto/[id].astro` | Vista detallada de proyecto |
| `/proyecto/[id]/aprobaciones` | `proyecto/[id]/aprobaciones.astro` | Aprobaciones del proyecto |
| `/proyecto/[id]/auditoria` | `proyecto/[id]/auditoria.astro` | Log de auditoría del proyecto |
| `/empleado-vista/[id]` | `empleado-vista/[id].astro` | Vista individual de empleado |
| `/tablero-empleados/[id]` | `tablero-empleados/[id].astro` | Tablero de empleados del proyecto |
| `/tablero-empleado-vista/[id]` | `tablero-empleado-vista/[id].astro` | Vista tablero individual |

### Rutas de Organizaciones

| Ruta | Archivo | Descripción |
|------|---------|-------------|
| `/organizaciones` | `organizaciones.astro` | Lista de organizaciones |
| `/organizations` | `organizations.astro` | Alias (redirección) |
| `/organizaciones/nueva` | `organizaciones/nueva.astro` | Crear organización |
| `/organizaciones/[id]/miembros` | `organizaciones/[id]/miembros.astro` | Miembros de la organización |
| `/organizaciones/[id]/proyectos` | `organizaciones/[id]/proyectos.astro` | Proyectos de la organización |
| `/organizaciones/[id]/settings` | `organizaciones/[id]/settings.astro` | Configuración de la organización |

---

## Sistema de Layouts

### BaseLayout

Layout general para todas las páginas. Incluye:
- `<head>` con meta tags y carga de CSS globales (`tokens.css` + `global.css`)
- `Header.astro` (navegación)
- `<slot />` para contenido de página
- Scripts globales de Alpine.js

### BrandedLayout

Extiende el concepto de BaseLayout para páginas de proyecto. Agrega:
- Variables CSS dinámicas con namespace `--brand-*`:
  - `--brand-primary`, `--brand-primary-dark`, `--brand-primary-light`
  - `--brand-accent`, `--brand-primary-rgb`
  - `--brand-background`, `--brand-text`, `--brand-border` (dark mode, heredan de `--tf-*`)
- Script que carga el `brand_color` del proyecto y sobreescribe las variables en runtime
- `data-project-id` en el `<body>` para contexto

---

## Handlers (Alpine.js)

Los handlers son módulos TypeScript que exportan funciones Alpine.js (`x-data`). Cada page tiene su handler correspondiente:

| Handler | Página/Componente |
|---------|-------------------|
| `login.ts` | Login |
| `register.ts` | Registro |
| `dashboard.ts` | Dashboard |
| `proyectos.ts` | Lista de proyectos |
| `proyecto.ts` | Vista de proyecto |
| `project-view.ts` | Sub-vista detallada |
| `nuevo-proyecto.ts` | Crear proyecto |
| `tarea.ts` | Gestión de tareas |
| `colaboradores.ts` | Colaboradores |
| `perfil.ts` | Perfil |
| `meses.ts` | Navegación por meses (sidebar) |
| `tablero-empleados.ts` | Tablero de empleados |
| `vista-empleado.ts` | Vista individual empleado |
| `gestion-empleados.ts` | Gestión de empleados |
| `asistencia.ts` | Marcado de asistencia |
| `configuracion-asistencia.ts` | Config de asistencia |
| `config-horarios.ts` | Config de horarios |
| `config-drawer.ts` | Drawer de configuración |
| `deudas.ts` | Deuda de horas |
| `justificativos-handler.ts` | Justificativos |
| `turnos-modal.ts` | Modal de turnos |
| `auth.ts` | Utilidades de auth |

---

## State Management

### Nanostores — `organizationStore.ts`

Store global que gestiona el contexto organizacional del usuario:

```typescript
interface Organization {
  id: number;
  nombre: string;
  slug: string;
  tipo_organizacion: 'personal' | 'empresa' | 'freelance' | 'agencia';
  plan_type: 'free' | 'starter' | 'professional' | 'enterprise';
  // ... más campos
}
```

Exports principales:
- `atom` para organización activa
- `map` para cache de organizaciones
- `computed` para derivados

Se usa desde cualquier componente o handler importando directamente.

---

## Services (API Client)

18 servicios en `src/services/` que encapsulan llamadas al backend:

| Servicio | Endpoint Base |
|----------|--------------|
| `api.ts` | Config base (URL, headers) |
| `auth.ts` | `/api/auth/*` |
| `proyectos.ts` | `/api/proyectos/*` |
| `tarea.ts` | `/api/tareas/*` |
| `colaboradores.ts` | `/api/colaboradores/*` |
| `dia.ts` | `/api/dias/*` |
| `empleados.ts` | `/api/empleados/*` |
| `usuarios.ts` | `/api/usuarios/*` |
| `organization.ts` / `organizationService.ts` | `/api/organizations/*` |
| `invitaciones.ts` | `/api/invitaciones/*` |
| `notificaciones.ts` | `/api/notificaciones/*` |
| `asistencia.ts` | `/api/asistencia/*` |
| `configuracion-asistencia.ts` | `/api/configuracion-asistencia/*` |
| `deudas.ts` | `/api/deuda/*` |
| `approvalService.ts` | `/api/aprobaciones/*` |
| `auditService.ts` | `/api/auditoria/*` |
| `budgetAddonService.ts` | `/api/budget-addons/*` |

---

## Accesibilidad (ARIA)

Estándares aplicados en la Fase 5:

| Patrón | Atributos | Dónde |
|--------|-----------|-------|
| Diálogos modales | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` | Modals, Drawers |
| Navegación | `role="navigation"`, `aria-label` | Header, Sidebar |
| Página actual | `aria-current="page"` | Links de navegación activos |
| Actualizaciones live | `aria-live="polite"` | Notificaciones, contadores |
| Formularios | `aria-label`, `aria-describedby` | Inputs sin label visible |
| Landmarks | `role="main"`, `role="banner"` | Layout estructural |
| Estado expandido | `aria-expanded` | Dropdowns, acordeones |

---

## Mapa de CSS

18 archivos CSS en `src/styles/`:

| Archivo | Scope | Importado por |
|---------|-------|---------------|
| `tokens.css` | **Global** — design tokens | `global.css` (indirecto, via `:root`) |
| `global.css` | **Global** — Tailwind + base + scrollbar | Todos los layouts |
| `auth.css` | Login, registro | `login.astro`, `register.astro` |
| `dashboard.css` | Dashboard | `dashboard.astro` |
| `proyectos.css` | Lista de proyectos | `proyectos.astro` |
| `proyecto.css` | Vista de proyecto | `proyecto/[id].astro` |
| `project-views.css` | Sub-vistas de proyecto | Varias páginas de proyecto |
| `nuevo-proyecto.css` | Formulario nuevo proyecto | `nuevo-proyecto.astro` |
| `tareas.css` | Tabla de tareas | Vista de proyecto |
| `tabla.css` | Tabla genérica | Múltiples vistas |
| `sidebar-meses.css` | Sidebar de meses | `ProjectSidebar.astro` |
| `modales.css` | Estilos base de modales | Componentes de modal |
| `invitaciones-modal.css` | Modal de invitaciones | `InvitacionesModal.astro` |
| `aprobaciones.css` | Vista de aprobaciones | `aprobaciones.astro` |
| `auditoria.css` | Vista de auditoría | `auditoria.astro` |
| `perfil.css` | Página de perfil | `perfil.astro` |
| `empleados-btn.css` | Botones de empleados | Vistas de empleados |
| `tablero-empleados.css` | Tablero de empleados | `tablero-empleados/[id].astro` |

---

## Convenciones de Naming

| Concepto | Convención | Ejemplo |
|----------|-----------|---------|
| Componentes | PascalCase `.astro` | `ProjectSidebar.astro` |
| Páginas | kebab-case `.astro` | `nuevo-proyecto.astro` |
| Handlers | kebab-case `.ts` | `tablero-empleados.ts` |
| Services | camelCase `.ts` | `approvalService.ts` |
| Tipos | PascalCase `.ts` | `Proyecto.ts` |
| CSS files | kebab-case `.css` | `sidebar-meses.css` |
| CSS tokens | `--tf-*` namespace | `--tf-color-primary` |
| Brand vars | `--brand-*` namespace | `--brand-primary` |
| CSS classes | `tf-` prefix para globales | `.tf-scrollbar` |
| Rutas dinámicas | `[param]` (Astro convention) | `[id].astro` |

---

## Middleware

### `middleware/auth.ts`

Middleware server-side de Astro que:
1. Lee el JWT de la cookie httpOnly
2. Valida el token contra el backend
3. Inyecta `locals.user` si es válido
4. Redirige a `/login` si la ruta es protegida y no hay auth
5. Rutas públicas: `/login`, `/register`, `/`, API endpoints
