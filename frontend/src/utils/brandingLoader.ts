/**
 * Project Branding Loader
 * Sistema de theming dinámico con CSS Variables
 * Fase 4: UX Unificada & Gestión Financiera
 *
 * Lógica diferencial:
 * - Personal/Freelance: Usa theme preference (dark/light)
 * - Empresa: Usa brand_color del proyecto
 */

interface BrandingConfig {
  primary: string;
  primaryDark: string;
  primaryLight: string;
  accent: string;
}

/**
 * Convierte HEX a HSL para manipulación de colores
 */
function hexToHSL(hex: string): { h: number; s: number; l: number } {
  // Remover #
  hex = hex.replace("#", "");

  // Convertir a RGB
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  const l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / d + 2) / 6;
        break;
      case b:
        h = ((r - g) / d + 4) / 6;
        break;
    }
  }

  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100),
  };
}

/**
 * Convierte HSL a HEX
 */
function hslToHex(h: number, s: number, l: number): string {
  l /= 100;
  const a = (s * Math.min(l, 1 - l)) / 100;
  const f = (n: number) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color)
      .toString(16)
      .padStart(2, "0");
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

/**
 * Genera variantes de color (dark y light)
 */
function generateColorShades(hexColor: string): BrandingConfig {
  const hsl = hexToHSL(hexColor);

  // Primary Dark: reducir luminosidad 20%
  const primaryDark = hslToHex(
    hsl.h,
    hsl.s,
    Math.max(hsl.l - 20, 10), // Mínimo 10% para evitar negro
  );

  // Primary Light: aumentar luminosidad 20%
  const primaryLight = hslToHex(
    hsl.h,
    hsl.s,
    Math.min(hsl.l + 20, 90), // Máximo 90% para evitar blanco
  );

  // Accent: rotar hue 30° para color complementario
  const accent = hslToHex((hsl.h + 30) % 360, hsl.s, hsl.l);

  return {
    primary: hexColor,
    primaryDark,
    primaryLight,
    accent,
  };
}

/**
 * Inyecta CSS Variables en el documento
 */
function injectCSSVariables(config: BrandingConfig): void {
  const root = document.documentElement;

  root.style.setProperty("--brand-primary", config.primary);
  root.style.setProperty("--brand-primary-dark", config.primaryDark);
  root.style.setProperty("--brand-primary-light", config.primaryLight);
  root.style.setProperty("--brand-accent", config.accent);

  // También actualizar Tailwind-compatible RGB values
  const primaryRGB = hexToRGB(config.primary);
  root.style.setProperty("--brand-primary-rgb", primaryRGB);
}

/**
 * Convierte HEX a RGB para Tailwind
 */
function hexToRGB(hex: string): string {
  hex = hex.replace("#", "");
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `${r}, ${g}, ${b}`;
}

/**
 * Detecta si la organización actual es personal/freelance
 */
function isCurrentOrgPersonal(): boolean {
  const orgType = localStorage.getItem("currentOrganizationType");
  return orgType === "personal" || orgType === "freelance";
}

/**
 * Carga el theme preference del usuario (personal mode)
 */
function loadUserThemePreference(): void {
  const theme = localStorage.getItem("themePreference") || "light";

  if (theme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

/**
 * Carga el branding del proyecto desde la API
 */
export async function loadProjectBranding(projectId: number): Promise<void> {
  // Si es organización personal, usar theme preference
  if (isCurrentOrgPersonal()) {
    loadUserThemePreference();
    return;
  }

  try {
    const token = localStorage.getItem("token");
    const orgId = localStorage.getItem("currentOrganizationId");

    const response = await fetch(
      `${import.meta.env.PUBLIC_API_BASE_URL || "http://localhost:22000"}/api/proyectos/${projectId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "X-Organization-ID": orgId || "",
        },
      },
    );

    if (!response.ok) {
      console.warn("Failed to load project branding");
      return;
    }

    const data = await response.json();
    const project = data.data || data;

    // Si el proyecto tiene brand_color, aplicarlo
    if (project.brand_color) {
      const colorConfig = generateColorShades(project.brand_color);
      injectCSSVariables(colorConfig);

      // Guardar en sessionStorage para persistencia durante la sesión
      sessionStorage.setItem(
        `project-${projectId}-branding`,
        JSON.stringify(colorConfig),
      );
    }
  } catch (error) {
    console.error("Error loading project branding:", error);
  }
}

/**
 * Restaura branding desde sessionStorage (más rápido)
 */
export function restoreProjectBranding(projectId: number): void {
  const cached = sessionStorage.getItem(`project-${projectId}-branding`);

  if (cached) {
    try {
      const config = JSON.parse(cached) as BrandingConfig;
      injectCSSVariables(config);
    } catch (error) {
      console.error("Error restoring branding from cache:", error);
    }
  }
}

/**
 * Reset a colores por defecto
 */
export function resetBranding(): void {
  const defaultConfig: BrandingConfig = {
    primary: "#3B82F6", // Indigo-600
    primaryDark: "#2563EB", // Indigo-700
    primaryLight: "#60A5FA", // Indigo-500
    accent: "#8B5CF6", // Purple-600
  };

  injectCSSVariables(defaultConfig);
}

/**
 * Hook para escuchar cambios de proyecto
 */
export function initBrandingListener(): void {
  // Escuchar eventos de navegación a proyecto
  window.addEventListener("projectChanged", ((event: CustomEvent) => {
    const projectId = event.detail?.projectId;
    if (projectId) {
      // Intentar restaurar desde cache primero
      restoreProjectBranding(projectId);
      // Luego cargar desde API (actualizar si cambió)
      loadProjectBranding(projectId);
    }
  }) as EventListener);

  // Detectar cambio de página (para SPAs)
  if (typeof window !== "undefined") {
    const pathname = window.location.pathname;
    const projectMatch = pathname.match(/\/proyecto\/(\d+)/);

    if (projectMatch) {
      const projectId = parseInt(projectMatch[1], 10);
      restoreProjectBranding(projectId);
      loadProjectBranding(projectId);
    }
  }
}

// Auto-inicializar en navegador
if (typeof window !== "undefined") {
  // Esperar a que el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBrandingListener);
  } else {
    initBrandingListener();
  }
}
