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
    background: '#1a1a2e',
    color: '#ffffff',
    confirmButtonColor: '#667eea',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading();
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
      background: '#1a1a2e',
      color: '#ffffff',
      confirmButtonColor: '#667eea',
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
