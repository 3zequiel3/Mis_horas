/**
 * Modal Management Utils - Centraliza lógica de modales reutilizable
 */

import Swal from 'sweetalert2';

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
    confirmButtonColor: options.isDangerous ? '#ef4444' : '#3b82f6',
    cancelButtonColor: '#6b7280',
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
    confirmButtonColor: '#10b981',
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
    confirmButtonColor: '#ef4444',
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
    confirmButtonColor: '#f59e0b',
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
    confirmButtonColor: '#3b82f6',
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
    didOpen: async () => {
      Swal.showLoading();
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
    didOpen: (toast) => {
      toast.addEventListener('mouseenter', Swal.stopTimer);
      toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
  });

  Toast.fire({
    icon: type,
    title: message,
  });
}
