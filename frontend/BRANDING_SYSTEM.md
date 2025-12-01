# Sistema de Branding Dinámico - Fase 4

## 📋 Descripción

Sistema de theming personalizado por proyecto usando CSS Variables. Permite que cada proyecto tenga su propio color de marca (`brand_color`) que se aplica automáticamente en toda la UI.

## 🎨 Características

### 1. **Lógica Diferencial**
- **Organizaciones Personal/Freelance**: Usa `themePreference` del usuario (light/dark)
- **Organizaciones Empresa**: Usa `brand_color` del proyecto activo

### 2. **CSS Variables Dinámicas**
```css
:root {
  --color-primary: #3b82f6;        /* Color principal del proyecto */
  --color-primary-dark: #2563eb;   /* Variante oscura (-20% luminosidad) */
  --color-primary-light: #60a5fa;  /* Variante clara (+20% luminosidad) */
  --color-accent: #8b5cf6;         /* Color complementario (+30° hue) */
  --color-primary-rgb: 59, 130, 246; /* RGB para Tailwind */
}
```

### 3. **Generación Automática de Variantes**
El sistema genera automáticamente:
- **Primary Dark**: Reduce luminosidad 20% (para hover, pressed states)
- **Primary Light**: Aumenta luminosidad 20% (para backgrounds suaves)
- **Accent**: Rota hue 30° (color complementario para highlights)

## 🚀 Uso

### En Layouts
```astro
---
import BrandedLayout from '@layouts/BrandedLayout.astro';
---

<BrandedLayout title="Mi Proyecto" projectId={proyecto.id}>
  <!-- Tu contenido -->
</BrandedLayout>
```

El layout automáticamente:
1. Restaura branding desde `sessionStorage` (rápido)
2. Carga branding actualizado desde API
3. Inyecta CSS Variables

### En Componentes (Tailwind)
```astro
<!-- Botones con color primario dinámico -->
<button class="bg-primary hover:bg-primary-dark text-white">
  Acción Principal
</button>

<!-- Badge con color de acento -->
<span class="bg-accent/10 text-accent">
  Destacado
</span>

<!-- Border con primary -->
<div class="border-2 border-primary">
  Contenido
</div>
```

### Llamadas Manuales
```typescript
import { 
  loadProjectBranding, 
  restoreProjectBranding, 
  resetBranding 
} from '@utils/brandingLoader';

// Cargar branding de proyecto
await loadProjectBranding(projectId);

// Restaurar desde cache (más rápido)
restoreProjectBranding(projectId);

// Resetear a colores por defecto
resetBranding();
```

## 🎯 Clases Tailwind Disponibles

### Backgrounds
```html
<div class="bg-primary">         <!-- Color principal -->
<div class="bg-primary-dark">    <!-- Variante oscura -->
<div class="bg-primary-light">   <!-- Variante clara -->
<div class="bg-accent">          <!-- Color de acento -->
```

### Text Colors
```html
<span class="text-primary">
<span class="text-primary-dark">
<span class="text-accent">
```

### Borders
```html
<div class="border-primary">
<div class="ring-primary">
```

### Paletas Completas
```html
<!-- Primary con escala 50-900 -->
<div class="bg-primary-500">     <!-- Usa CSS variable -->
<div class="bg-primary-700">     <!-- Usa CSS variable dark -->

<!-- Accent con escala 50-900 -->
<div class="bg-accent-600">      <!-- Usa CSS variable -->
```

## 🔧 Configuración en Proyecto

### 1. En Base de Datos
```sql
UPDATE proyectos 
SET brand_color = '#10B981',  -- Verde
    client_name = 'Cliente ABC'
WHERE id = 1;
```

### 2. En UI (ProjectSettingsDrawer)
Tab **General** → Campo **Color de marca**:
- 6 presets rápidos
- Picker de color personalizado
- Input HEX manual

### 3. En Wizard (SuperWizard)
Paso 1 **Identidad** → Campo **Color de marca**:
- Selección de color al crear proyecto
- Preset colors disponibles

## 📦 Estructura de Archivos

```
frontend/src/
├── utils/
│   └── brandingLoader.ts          # Lógica principal
├── layouts/
│   └── BrandedLayout.astro        # Layout con auto-init
└── styles/
    └── branding.css               # CSS variables (opcional)
```

## 🎨 Colores por Defecto

Si no se define `brand_color` o falla la carga:
- **Primary**: `#3B82F6` (Indigo 600)
- **Primary Dark**: `#2563EB` (Indigo 700)
- **Primary Light**: `#60A5FA` (Indigo 500)
- **Accent**: `#8B5CF6` (Purple 600)

## 🔄 Cache y Persistencia

### SessionStorage
El branding se guarda en `sessionStorage` por sesión:
```
project-{id}-branding = {
  primary: "#10B981",
  primaryDark: "#059669",
  primaryLight: "#34D399",
  accent: "#3B82F6"
}
```

**Ventajas**:
- Carga instantánea al navegar
- Se actualiza desde API en background
- Se limpia al cerrar sesión

### LocalStorage (Theme Preference)
Solo para organizaciones personal/freelance:
```
themePreference = "light" | "dark"
```

## 🎭 Ejemplos de Uso

### Botón con branding
```astro
<button class="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg transition-colors">
  Guardar Proyecto
</button>
```

### Card con borde de marca
```astro
<div class="border-l-4 border-primary bg-primary-light/10 p-4 rounded">
  <h3 class="text-primary-dark font-semibold">Nota Importante</h3>
  <p class="text-gray-700">Contenido de la nota...</p>
</div>
```

### Badge con acento
```astro
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-accent text-white">
  Nuevo
</span>
```

### Progress bar con gradiente
```astro
<div class="h-2 bg-gray-200 rounded-full overflow-hidden">
  <div 
    class="h-full bg-gradient-to-r from-primary to-accent"
    style="width: 65%"
  ></div>
</div>
```

## 🔍 Debugging

### Verificar variables actuales
```javascript
// En DevTools Console
const root = document.documentElement;
console.log(getComputedStyle(root).getPropertyValue('--color-primary'));
```

### Forzar recarga
```javascript
import { loadProjectBranding } from '@utils/brandingLoader';

// Forzar desde API (ignora cache)
await loadProjectBranding(projectId);
```

## ⚠️ Consideraciones

1. **Contraste**: Los colores generados mantienen ratios aceptables, pero verifica contraste para accesibilidad
2. **Performance**: Primera carga desde API (~100ms), luego instantáneo desde cache
3. **Fallback**: Siempre hay colores por defecto si falla
4. **SSR**: Las variables se inyectan client-side, no en SSR

## 🚀 Próximas Mejoras

- [ ] Validación de contraste WCAG AA
- [ ] Preview en tiempo real en settings drawer
- [ ] Temas predefinidos (Material, Nord, Dracula)
- [ ] Exportar/Importar paletas completas
- [ ] Dark mode automático por proyecto

---

**Implementado en**: Fase 4 - UX Unificada & Gestión Financiera
**Versión**: 1.0.0
**Última actualización**: 2024
