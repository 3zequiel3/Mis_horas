# TimeFlow — Design Tokens

## Filosofía

Los design tokens de TimeFlow siguen un principio simple: **una sola fuente de verdad**.

Todas las decisiones de color, espaciado, bordes y sombras se definen en **un solo archivo** (`tokens.css`) bajo el namespace `--tf-*`. Ningún otro archivo CSS declara valores de color directamente — todo referencia tokens.

Este approach garantiza:
- **Consistencia**: cambiar un token actualiza TODA la UI
- **Mantenibilidad**: no hay colores hardcodeados dispersos en 18 archivos CSS
- **Theming futuro**: sería trivial agregar un light mode cambiando solo `tokens.css`

---

## Tabla Completa de Tokens

### Brand

| Token | Valor | Uso |
|-------|-------|-----|
| `--tf-color-primary` | `#667eea` | Color principal de la marca — botones, links, acentos |
| `--tf-color-primary-hover` | `#5a6fe0` | Hover state del primary |
| `--tf-color-accent` | `#ff5757` | Color de acento — acciones destructivas, badges urgentes |
| `--tf-color-accent-hover` | `#ff6b6b` | Hover state del accent |

### Semánticos

| Token | Valor | Uso |
|-------|-------|-----|
| `--tf-color-success` | `#10b981` | Éxito, aprobado, positivo (verde Emerald) |
| `--tf-color-danger` | `#ef4444` | Error, eliminación, peligro (rojo) |
| `--tf-color-warning` | `#f59e0b` | Advertencia, atención (amarillo Amber) |
| `--tf-color-info` | `#3b82f6` | Información, neutral destacado (azul) |

### Superficies (Dark Theme)

| Token | Valor | Uso |
|-------|-------|-----|
| `--tf-bg-base` | `#0f1419` | Fondo de la página (el más oscuro) |
| `--tf-bg-surface` | `#1a1a2e` | Tarjetas, paneles, contenedores |
| `--tf-bg-elevated` | `#16213e` | Elementos elevados (dropdowns, tooltips, headers) |
| `--tf-bg-input` | `rgba(255, 255, 255, 0.05)` | Fondo de inputs y fields |

### Texto

| Token | Valor | Uso |
|-------|-------|-----|
| `--tf-text-primary` | `#f1f5f9` | Texto principal (casi blanco) |
| `--tf-text-secondary` | `#94a3b8` | Texto secundario (gris claro) |
| `--tf-text-muted` | `#64748b` | Texto muted, labels, placeholders |

### Bordes

| Token | Valor | Uso |
|-------|-------|-----|
| `--tf-border` | `rgba(255, 255, 255, 0.1)` | Borde por defecto (sutil, 10% blanco) |
| `--tf-border-hover` | `rgba(255, 255, 255, 0.2)` | Borde en hover (20% blanco) |

### Sombras

| Token | Valor | Uso |
|-------|-------|-----|
| `--tf-shadow-sm` | `0 1px 2px 0 rgba(0,0,0,0.3)` | Sombra leve — botones, badges |
| `--tf-shadow-md` | `0 4px 6px -1px rgba(0,0,0,0.4)` | Sombra media — tarjetas, dropdowns |
| `--tf-shadow-lg` | `0 10px 25px -5px rgba(0,0,0,0.5)` | Sombra fuerte — modales, drawers |

### Radii (Border Radius)

| Token | Valor | Uso |
|-------|-------|-----|
| `--tf-radius-sm` | `6px` | Botones pequeños, badges, chips |
| `--tf-radius-md` | `8px` | Botones, inputs, tarjetas pequeñas |
| `--tf-radius-lg` | `12px` | Tarjetas, paneles, contenedores |
| `--tf-radius-xl` | `16px` | Modales, drawers, cards grandes |

---

## Mapeo a Tailwind 4

En `global.css`, el bloque `@theme` conecta tokens con utilidades Tailwind:

```css
@import "tailwindcss";

@theme {
  --color-primary: var(--tf-color-primary);
  --color-primary-hover: var(--tf-color-primary-hover);
  --color-accent: var(--tf-color-accent);
  --color-accent-hover: var(--tf-color-accent-hover);

  --color-success: var(--tf-color-success);
  --color-danger: var(--tf-color-danger);
  --color-warning: var(--tf-color-warning);
  --color-info: var(--tf-color-info);

  --color-surface: var(--tf-bg-surface);
  --color-elevated: var(--tf-bg-elevated);
  --color-base: var(--tf-bg-base);

  --color-tf-text: var(--tf-text-primary);
  --color-tf-text-secondary: var(--tf-text-secondary);
  --color-tf-text-muted: var(--tf-text-muted);
  --color-tf-border: var(--tf-border);

  --radius-sm: var(--tf-radius-sm);
  --radius-md: var(--tf-radius-md);
  --radius-lg: var(--tf-radius-lg);
  --radius-xl: var(--tf-radius-xl);
}
```

Esto permite escribir en el HTML:

```html
<!-- En vez de: style="background: var(--tf-bg-surface)" -->
<div class="bg-surface text-tf-text rounded-lg border border-tf-border">
  <h2 class="text-primary">Título</h2>
  <p class="text-tf-text-secondary">Descripción</p>
  <button class="bg-primary hover:bg-primary-hover rounded-md">
    Guardar
  </button>
</div>
```

---

## BrandedLayout — Theming Dinámico por Proyecto

Para páginas de proyecto, existe un segundo set de variables con namespace `--brand-*`. Estas se cargan dinámicamente según el `brand_color` del proyecto.

### Variables de Brand

| Variable | Default | Descripción |
|----------|---------|-------------|
| `--brand-primary` | `#3b82f6` | Color principal del proyecto |
| `--brand-primary-dark` | `#2563eb` | Variante oscura |
| `--brand-primary-light` | `#60a5fa` | Variante clara |
| `--brand-accent` | `#8b5cf6` | Acento del proyecto |
| `--brand-primary-rgb` | `59, 130, 246` | RGB para usar con `rgba()` |
| `--brand-background` | hereda `--tf-bg-base` | Fondo en dark mode |
| `--brand-text` | hereda `--tf-text-primary` | Texto en dark mode |
| `--brand-border` | hereda `--tf-border` | Bordes en dark mode |

### ¿Cómo funciona?

1. `BrandedLayout.astro` define defaults en un `<style is:inline>`
2. Un script carga `loadProjectBranding()` que hace fetch del color del proyecto
3. Sobreescribe las `--brand-*` variables en runtime
4. Los CSS de proyecto usan `--brand-*` en vez de `--tf-*` para elementos temáticos

### ¿Por qué namespace separado?

Para evitar colisión: `--tf-*` son GLOBALES e inmutables. `--brand-*` son LOCALES al proyecto y dinámicas. Si usáramos `--tf-color-primary` para branding, cambiar el color de un proyecto afectaría toda la app.

---

## Guía de Migración: Variables Legacy → Tokens

Durante la Fase 5 se migraron todas las variables CSS antiguas al namespace `--tf-*`. Referencia:

| Variable Vieja | Token Nuevo |
|----------------|-------------|
| `--primary`, `--primary-color` | `--tf-color-primary` |
| `--primary-hover` | `--tf-color-primary-hover` |
| `--accent` | `--tf-color-accent` |
| `--bg-dark`, `--dark-bg` | `--tf-bg-base` |
| `--bg-card`, `--card-bg` | `--tf-bg-surface` |
| `--bg-header` | `--tf-bg-elevated` |
| `--text-primary`, `--text-color` | `--tf-text-primary` |
| `--text-secondary`, `--text-muted` | `--tf-text-secondary` |
| `--border-color` | `--tf-border` |
| `--shadow-sm` | `--tf-shadow-sm` |
| `--radius-md` (sin prefijo) | `--tf-radius-md` |

> Si encontrás alguna referencia a variables sin el prefijo `--tf-`, es legacy y debería migrarse.

---

## Ejemplos de Uso

### En CSS con @layer components

```css
@layer components {
  .card {
    background: var(--tf-bg-surface);
    border: 1px solid var(--tf-border);
    border-radius: var(--tf-radius-lg);
    padding: 1.5rem;
    box-shadow: var(--tf-shadow-md);
  }

  .card:hover {
    border-color: var(--tf-border-hover);
  }

  .btn-primary {
    background: var(--tf-color-primary);
    color: var(--tf-text-primary);
    border-radius: var(--tf-radius-md);
    padding: 0.5rem 1rem;
  }

  .btn-primary:hover {
    background: var(--tf-color-primary-hover);
  }

  .btn-danger {
    background: var(--tf-color-danger);
    color: var(--tf-text-primary);
  }

  .status-badge--success {
    background: var(--tf-color-success);
  }

  .status-badge--warning {
    background: var(--tf-color-warning);
  }
}
```

### En HTML con Tailwind utilities

```html
<!-- Tarjeta -->
<div class="bg-surface border border-tf-border rounded-lg p-6 shadow-md">
  <h3 class="text-tf-text font-semibold">Proyecto X</h3>
  <p class="text-tf-text-secondary text-sm">Descripción del proyecto</p>
</div>

<!-- Botón primary -->
<button class="bg-primary hover:bg-primary-hover text-white rounded-md px-4 py-2">
  Crear
</button>

<!-- Badge de estado -->
<span class="bg-success text-white text-xs px-2 py-1 rounded-sm">
  Activo
</span>
```

### Colores semánticos en contexto

```html
<!-- Mensaje de error -->
<div class="bg-danger/10 border border-danger text-danger rounded-md p-3">
  Error: No se pudo guardar
</div>

<!-- Mensaje de éxito -->
<div class="bg-success/10 border border-success text-success rounded-md p-3">
  Guardado exitosamente
</div>
```

---

## Reglas de Diseño

1. **NO gradientes**: TODOS los fondos son colores sólidos flat. Sin `linear-gradient()`.
2. **Profundidad con bordes**: La jerarquía visual se logra con `--tf-border` + `--tf-shadow-*`, no con gradientes.
3. **3 niveles de superficie**: `base` (fondo) → `surface` (tarjetas) → `elevated` (overlays). Nada más.
4. **3 niveles de texto**: `primary` → `secondary` → `muted`. Usar consistentemente.
5. **Namespace obligatorio**: Toda variable nueva DEBE tener prefijo `--tf-*`. Variables sin prefijo son legacy.
6. **Un token, un lugar**: Si un valor aparece en más de un archivo CSS, debería ser un token.
7. **@layer components**: Todo estilo custom va dentro de `@layer components`. Nunca estilos sueltos que compitan con Tailwind.
8. **Dark-first**: El sistema está diseñado dark-first. Los tokens asumen fondo oscuro.
