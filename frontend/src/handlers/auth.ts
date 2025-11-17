/**
 * Handlers para logout
 */

import { AuthService } from '../services/auth';
import Swal from 'sweetalert2';

export async function logout(): Promise<void> {
  // Mostrar modal de carga mientras se procesa el logout
  const loadingModal = Swal.fire({
    title: 'Cerrando sesión...',
    icon: 'info',
    background: '#0f1419',
    color: '#c8c8c8',
    confirmButtonColor: '#667eea',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading();
      const loader = document.querySelector('.swal2-loader') as HTMLElement;
      if (loader) loader.style.borderColor = '#667eea';
    }
  });

  try {
    // Llamar al logout del AuthService
    await AuthService.logout();

    // Mostrar mensaje de éxito
    await Swal.fire({
      title: 'Sesión Cerrada',
      text: 'Redirigiendo a login...',
      icon: 'success',
      background: '#0f1419',
      color: '#c8c8c8',
      confirmButtonColor: '#10b981',
      iconColor: '#10b981',
      timer: 1500,
      timerProgressBar: true,
    });

    // Redirigir a login
    window.location.href = '/login';
  } catch (error) {
    Swal.hideLoading();
    throw error;
  }
}

export const authHandlers = {
  logout,
};
