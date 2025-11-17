/**
 * Modal Management Utils - Centraliza lógica de modales reutilizable
 */

import Swal from 'sweetalert2';

// Configuración de tema oscuro para Sweet Alert
const darkThemeConfig = {
  background: '#0f1419',
  color: '#c8c8c8',
  confirmButtonColor: '#667eea',
  cancelButtonColor: '#2d3746',
  iconColor: '#667eea',
};

export interface ModalOptions {
  title: string;
  message?: string;
  type?: 'success' | 'error' | 'warning' | 'info' | 'question';
  confirmText?: string;
  cancelText?: string;
  isDangerous?: boolean;
}

/**
 * Muestra un modal de confirmación
 */
export async function showConfirmModal(options: ModalOptions): Promise<boolean> {
  const result = await Swal.fire({
    title: options.title,
    text: options.message,
    icon: options.type || 'question',
    confirmButtonText: options.confirmText || 'Confirmar',
    cancelButtonText: options.cancelText || 'Cancelar',
    showCancelButton: true,
    background: darkThemeConfig.background,
    color: darkThemeConfig.color,
    confirmButtonColor: options.isDangerous ? '#ef4444' : '#667eea',
    cancelButtonColor: darkThemeConfig.cancelButtonColor,
    iconColor: options.type === 'success' ? '#10b981' : options.type === 'error' ? '#ef4444' : '#667eea',
  });

  return result.isConfirmed;
}

/**
 * Muestra un modal de éxito
 */
export async function showSuccessModal(title: string, message?: string): Promise<void> {
  await Swal.fire({
    title,
    text: message,
    icon: 'success',
    background: darkThemeConfig.background,
    color: darkThemeConfig.color,
    confirmButtonColor: '#10b981',
    iconColor: '#10b981',
  });
}

/**
 * Muestra un modal de error
 */
export async function showErrorModal(title: string, message?: string): Promise<void> {
  await Swal.fire({
    title,
    text: message,
    icon: 'error',
    background: darkThemeConfig.background,
    color: darkThemeConfig.color,
    confirmButtonColor: '#ef4444',
    iconColor: '#ef4444',
  });
}

/**
 * Muestra un modal de advertencia
 */
export async function showWarningModal(title: string, message?: string): Promise<boolean> {
  const result = await Swal.fire({
    title,
    text: message,
    icon: 'warning',
    confirmButtonText: 'Continuar',
    cancelButtonText: 'Cancelar',
    showCancelButton: true,
    background: darkThemeConfig.background,
    color: darkThemeConfig.color,
    confirmButtonColor: '#f59e0b',
    cancelButtonColor: darkThemeConfig.cancelButtonColor,
    iconColor: '#f59e0b',
  });

  return result.isConfirmed;
}

/**
 * Muestra un modal de información
 */
export async function showInfoModal(title: string, message?: string): Promise<void> {
  await Swal.fire({
    title,
    text: message,
    icon: 'info',
    background: darkThemeConfig.background,
    color: darkThemeConfig.color,
    confirmButtonColor: '#667eea',
    iconColor: '#667eea',
  });
}

/**
 * Muestra modal con carga
 */
export function showLoadingModal(title: string = 'Cargando...'): void {
  Swal.fire({
    title,
    allowOutsideClick: false,
    allowEscapeKey: false,
    background: darkThemeConfig.background,
    color: darkThemeConfig.color,
    didOpen: async () => {
      Swal.showLoading();
      const loader = document.querySelector('.swal2-loader') as HTMLElement;
      if (loader) loader.style.borderColor = '#667eea';
    },
  });
}

/**
 * Cierra el modal activo
 */
export function closeModal(): void {
  Swal.close();
}

/**
 * Muestra un toast (notificación pequeña)
 */
export function showToast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
  const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    background: darkThemeConfig.background,
    color: darkThemeConfig.color,
    didOpen: (toast) => {
      toast.addEventListener('mouseenter', Swal.stopTimer);
      toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
  });

  const iconColor = type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#667eea';
  Toast.fire({
    icon: type,
    title: message,
    iconColor,
  });
}
