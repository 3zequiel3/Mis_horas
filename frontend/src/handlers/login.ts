/**
 * Handler de Login - Gestión del inicio de sesión
 */

import { AuthService } from '../services/auth';
import { AlertUtils } from '../utils/swal';

export const LoginHandler = {
  /**
   * Valida que los campos requeridos estén llenos
   */
  validarCampos(username: string, password: string): boolean {
    if (!username.trim() || !password.trim()) {
      AlertUtils.error('Error', 'Por favor completa todos los campos');
      return false;
    }
    return true;
  },

  /**
   * Realiza el login del usuario
   */
  async login() {
    try {
      const username = (document.getElementById('username') as HTMLInputElement).value;
      const password = (document.getElementById('password') as HTMLInputElement).value;
      const rememberMe = (document.getElementById('remember-me') as HTMLInputElement).checked;

      // Validar
      if (!this.validarCampos(username, password)) {
        return false;
      }

      // Hacer login
      await AuthService.login(username, password, rememberMe);

      // Mostrar éxito y redirigir
      this.mostrarMensajeExito();
      return true;
    } catch (error) {
      console.error('Error:', error);
      this.mostrarMensajeError((error as Error).message);
      await AlertUtils.error('Error', (error as Error).message);
      return false;
    }
  },

  /**
   * Muestra mensaje de éxito y redirige
   */
  async mostrarMensajeExito() {
    await AlertUtils.fire({
      title: '¡Bienvenido!',
      text: 'Iniciando sesión...',
      icon: 'success',
      didOpen: () => {
        AlertUtils.close();
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1000);
      },
    });
  },

  /**
   * Muestra mensaje de error
   */
  mostrarMensajeError(mensaje: string) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
      errorDiv.textContent = mensaje;
      errorDiv.style.display = 'block';
    }
  },
};
