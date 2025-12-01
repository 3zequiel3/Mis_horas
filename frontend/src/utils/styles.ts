/**
 * CSS/Tailwind Utilities
 * Clases y helpers reutilizables para estilos consistentes
 */

// Colores consistentes con el tema
export const THEME_COLORS = {
  // Primary
  primary: {
    DEFAULT: '#667eea',
    light: '#764ba2',
    dark: '#5568d3',
  },
  
  // Success
  success: {
    DEFAULT: '#10b981',
    light: '#34d399',
    dark: '#059669',
  },
  
  // Error
  error: {
    DEFAULT: '#ef4444',
    light: '#f87171',
    dark: '#dc2626',
  },
  
  // Warning
  warning: {
    DEFAULT: '#f59e0b',
    light: '#fbbf24',
    dark: '#d97706',
  },
  
  // Info
  info: {
    DEFAULT: '#3b82f6',
    light: '#60a5fa',
    dark: '#2563eb',
  },
  
  // Grays
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
} as const;

// Clases de botones reutilizables
export const BUTTON_CLASSES = {
  primary: 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-medium px-4 py-2 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg',
  secondary: 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-medium px-4 py-2 rounded-lg transition-colors',
  success: 'bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded-lg transition-colors',
  danger: 'bg-red-600 hover:bg-red-700 text-white font-medium px-4 py-2 rounded-lg transition-colors',
  warning: 'bg-yellow-600 hover:bg-yellow-700 text-white font-medium px-4 py-2 rounded-lg transition-colors',
  outline: 'border-2 border-gray-300 dark:border-gray-600 hover:border-indigo-600 text-gray-900 dark:text-white font-medium px-4 py-2 rounded-lg transition-colors',
  ghost: 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-900 dark:text-white font-medium px-4 py-2 rounded-lg transition-colors',
  link: 'text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium underline',
} as const;

// Clases de cards reutilizables
export const CARD_CLASSES = {
  default: 'bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700',
  hover: 'bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow',
  interactive: 'bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-indigo-500 transition-all cursor-pointer',
} as const;

// Clases de badges
export const BADGE_CLASSES = {
  default: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
  success: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  error: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  warning: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  info: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  primary: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
} as const;

// Clases de alerts
export const ALERT_CLASSES = {
  success: 'bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500 text-green-800 dark:text-green-200 p-4 rounded',
  error: 'bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 text-red-800 dark:text-red-200 p-4 rounded',
  warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 text-yellow-800 dark:text-yellow-200 p-4 rounded',
  info: 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 text-blue-800 dark:text-blue-200 p-4 rounded',
} as const;

// Clases de inputs
export const INPUT_CLASSES = {
  default: 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors',
  error: 'w-full px-4 py-2 border border-red-500 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:border-red-500',
  success: 'w-full px-4 py-2 border border-green-500 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-green-500',
} as const;

// Clases de modales
export const MODAL_CLASSES = {
  overlay: 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40 flex items-center justify-center',
  container: 'bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden',
  header: 'px-6 py-4 border-b border-gray-200 dark:border-gray-700',
  body: 'px-6 py-4 overflow-y-auto max-h-[60vh]',
  footer: 'px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3',
} as const;

// Clases de tablas
export const TABLE_CLASSES = {
  container: 'overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700',
  table: 'min-w-full divide-y divide-gray-200 dark:divide-gray-700',
  thead: 'bg-gray-50 dark:bg-gray-900',
  th: 'px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider',
  tbody: 'bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700',
  td: 'px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100',
} as const;

// Clases de animaciones
export const ANIMATION_CLASSES = {
  fadeIn: 'animate-fade-in',
  fadeOut: 'animate-fade-out',
  slideIn: 'animate-slide-in',
  slideOut: 'animate-slide-out',
  pulse: 'animate-pulse',
  spin: 'animate-spin',
  bounce: 'animate-bounce',
} as const;

// Helpers para construir clases
export function cn(...classes: (string | false | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Genera clases de botón con variantes
 */
export function getButtonClass(
  variant: keyof typeof BUTTON_CLASSES = 'primary',
  size: 'sm' | 'md' | 'lg' = 'md',
  fullWidth = false
): string {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  return cn(
    BUTTON_CLASSES[variant],
    sizeClasses[size],
    fullWidth && 'w-full'
  );
}

/**
 * Genera clases de card con variantes
 */
export function getCardClass(
  variant: keyof typeof CARD_CLASSES = 'default',
  padding: 'none' | 'sm' | 'md' | 'lg' = 'md'
): string {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
  
  return cn(CARD_CLASSES[variant], paddingClasses[padding]);
}

/**
 * Genera clases de badge con variante
 */
export function getBadgeClass(variant: keyof typeof BADGE_CLASSES = 'default'): string {
  return BADGE_CLASSES[variant];
}

/**
 * Genera clases de alert con variante
 */
export function getAlertClass(variant: keyof typeof ALERT_CLASSES): string {
  return ALERT_CLASSES[variant];
}
