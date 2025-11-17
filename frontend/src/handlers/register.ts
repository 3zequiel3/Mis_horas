/**
 * Handler de Registro - Gestión del registro de nuevos usuarios
 */

import { AuthService } from '../services/auth';
import { AlertUtils } from '../utils/swal';

export const RegisterHandler = {
  /**
   * Valida que las contraseñas coincidan
   */
  validarContraseñas(password: string, passwordConfirm: string): boolean {
    if (password !== passwordConfirm) {
      AlertUtils.error('Error', 'Las contraseñas no coinciden');
      return false;
    }
    return true;
  },

  /**
   * Valida que todos los campos requeridos estén llenos
   */
  validarCampos(username: string, email: string, password: string): boolean {
    if (!username.trim() || !email.trim() || !password.trim()) {
      AlertUtils.error('Error', 'Por favor completa todos los campos requeridos');
      return false;
    }
    return true;
  },

  /**
   * Registra un nuevo usuario
   */
  async registrar() {
    try {
      const username = (document.getElementById('username') as HTMLInputElement).value;
      const email = (document.getElementById('email') as HTMLInputElement).value;
      const nombre_completo = (document.getElementById('nombre_completo') as HTMLInputElement).value;
      const password = (document.getElementById('password') as HTMLInputElement).value;
      const passwordConfirm = (document.getElementById('password-confirm') as HTMLInputElement).value;

      // Validaciones
      if (!this.validarCampos(username, email, password)) {
        return false;
      }

      if (!this.validarContraseñas(password, passwordConfirm)) {
        return false;
      }

      // Registrar
      await AuthService.register(username, email, password, nombre_completo);

      // Mostrar éxito y redirigir
      this.mostrarMensajeExito();
      return true;
    } catch (error) {
      console.error('Error:', error);
      this.mostrarMensajeError((error as Error).message);
      await AlertUtils.error('Error al Registrar', (error as Error).message);
      return false;
    }
  },

  /**
   * Muestra mensaje de éxito y redirige
   */
  mostrarMensajeExito() {
    const successDiv = document.getElementById('success-message');
    if (successDiv) {
      successDiv.textContent = '✅ Cuenta creada exitosamente. Redirigiendo al login...';
      successDiv.style.display = 'block';
    }

    // Redirigir después de 1.5s
    setTimeout(() => {
      window.location.href = '/login';
    }, 1500);
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
