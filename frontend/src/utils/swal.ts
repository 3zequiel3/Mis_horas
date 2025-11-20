import Swal from 'sweetalert2';

/**
 * Configuración base para SweetAlert2 en modo oscuro
 */
const DARK_THEME_CONFIG = {
  background: '#0f1419',
  color: '#c8c8c8',
  confirmButtonColor: '#667eea',
  cancelButtonColor: '#2d3746',
  iconColor: '#667eea',
};

/**
 * SweetAlert utilities con tema oscuro por defecto
 */
export const AlertUtils = {
  /**
   * Alerta de éxito
   */
  success: (title: string, text?: string) => {
    return Swal.fire({
      title,
      text,
      icon: 'success',
      ...DARK_THEME_CONFIG,
      iconColor: '#10b981',
      confirmButtonColor: '#10b981',
    });
  },

  /**
   * Alerta de error
   */
  error: (title: string, text?: string) => {
    return Swal.fire({
      title,
      text,
      icon: 'error',
      ...DARK_THEME_CONFIG,
      iconColor: '#ef4444',
      confirmButtonColor: '#ef4444',
    });
  },

  /**
   * Alerta de advertencia
   */
  warning: (title: string, text?: string) => {
    return Swal.fire({
      title,
      text,
      icon: 'warning',
      ...DARK_THEME_CONFIG,
      iconColor: '#f59e0b',
    });
  },

  /**
   * Alerta de información
   */
  info: (title: string, text?: string) => {
    return Swal.fire({
      title,
      text,
      icon: 'info',
      ...DARK_THEME_CONFIG,
      iconColor: '#3b82f6',
      confirmButtonColor: '#3b82f6',
    });
  },

  /**
   * Alerta de pregunta (confirmación)
   */
  question: (title: string, text?: string) => {
    return Swal.fire({
      title,
      text,
      icon: 'question',
      showCancelButton: true,
      ...DARK_THEME_CONFIG,
      confirmButtonText: 'Sí',
      cancelButtonText: 'Cancelar',
    });
  },

  /**
   * Confirmación personalizada
   */
  confirm: (title: string, text?: string, confirmText = 'Confirmar', cancelText = 'Cancelar') => {
    return Swal.fire({
      title,
      text,
      icon: 'question',
      showCancelButton: true,
      ...DARK_THEME_CONFIG,
      confirmButtonText: confirmText,
      cancelButtonText: cancelText,
    });
  },

  /**
   * Alerta de carga con spinner
   */
  loading: (title: string, text?: string) => {
    Swal.fire({
      title,
      text,
      ...DARK_THEME_CONFIG,
      didOpen: () => {
        Swal.showLoading();
      },
      allowOutsideClick: false,
      allowEscapeKey: false,
    });
  },

  /**
   * Cerrar la alerta actual
   */
  close: () => {
    Swal.close();
  },

  /**
   * Alerta personalizada con configuración completa
   */
  fire: (config: any) => {
    return Swal.fire({
      ...DARK_THEME_CONFIG,
      ...config,
    });
  },

  /**
   * Toast (notificación en esquina)
   */
  toast: (
    title: string,
    icon: 'success' | 'error' | 'warning' | 'info' = 'success',
    position: 'top-start' | 'top' | 'top-end' | 'center-start' | 'center' | 'center-end' | 'bottom-start' | 'bottom' | 'bottom-end' = 'top-end'
  ) => {
    return Swal.fire({
      title,
      icon,
      toast: true,
      position,
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer);
        toast.addEventListener('mouseleave', Swal.resumeTimer);
      },
      ...DARK_THEME_CONFIG,
      background: '#1a1a2e',
      color: '#c8c8c8',
    });
  },

  /**
   * Prompt con input
   */
  prompt: (
    title: string,
    text?: string,
    inputType: 'text' | 'email' | 'textarea' = 'text',
    inputPlaceholder?: string
  ) => {
    return Swal.fire({
      title,
      text,
      input: inputType,
      inputPlaceholder,
      showCancelButton: true,
      confirmButtonText: 'Aceptar',
      cancelButtonText: 'Cancelar',
      ...DARK_THEME_CONFIG,
    });
  },
};

export default AlertUtils;
