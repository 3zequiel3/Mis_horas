// Gestión del registro de nuevos usuarios

import { AuthService } from '../services/auth';
import { AlertUtils } from '../utils/swal';
import { validateRequired, validateEmail, validatePasswordMatch, validatePassword, validateAll } from '../utils/validation';

export const RegisterHandler = {
  // Valida que las contraseñas coincidan
  validarContraseñas(password: string, passwordConfirm: string): boolean {
    const validation = validatePasswordMatch(password, passwordConfirm);
    if (!validation.valid) {
      AlertUtils.error('Error', validation.message!);
      return false;
    }
    return true;
  },

  // Valida que todos los campos requeridos estén llenos
  validarCampos(username: string, email: string, password: string): boolean {
    const validation = validateAll(
      validateRequired(username, 'Usuario'),
      validateRequired(email, 'Email'),
      validateEmail(email),
      validateRequired(password, 'Contraseña'),
      validatePassword(password, 8)
    );
    
    if (!validation.valid) {
      AlertUtils.error('Error', validation.message!);
      return false;
    }
    return true;
  },

  // Registra un nuevo usuario en el sistema
  async registrar() {
    try {
      const username = (document.getElementById('username') as HTMLInputElement).value;
      const email = (document.getElementById('email') as HTMLInputElement).value;
      const nombre_completo = (document.getElementById('nombre_completo') as HTMLInputElement).value;
      const password = (document.getElementById('password') as HTMLInputElement).value;
      const passwordConfirm = (document.getElementById('password-confirm') as HTMLInputElement).value;
      const tokenInvitacion = (document.getElementById('token_invitacion') as HTMLInputElement)?.value || '';

      // Validaciones
      if (!this.validarCampos(username, email, password)) {
        return false;
      }

      if (!this.validarContraseñas(password, passwordConfirm)) {
        return false;
      }

      // Registrar (ahora devuelve token y auto-inicia sesión)
      const response = await AuthService.register(username, email, password, nombre_completo, tokenInvitacion);

      // Mostrar éxito y redirigir
      this.mostrarMensajeExito(response.proyecto_id);
      return true;
    } catch (error) {
      console.error('Error:', error);
      this.mostrarMensajeError((error as Error).message);
      await AlertUtils.error('Error al Registrar', (error as Error).message);
      return false;
    }
  },

  // Muestra mensaje de éxito y redirige al dashboard o proyecto (sesión iniciada)
  mostrarMensajeExito(proyectoId?: number) {
    const successDiv = document.getElementById('success-message');
    const mensaje = proyectoId 
      ? '✅ Cuenta creada e invitación aceptada. Redirigiendo al proyecto...'
      : '✅ Cuenta creada exitosamente. Redirigiendo...';
    
    if (successDiv) {
      successDiv.textContent = mensaje;
      successDiv.style.display = 'block';
    }

    // Redirigir después de 1.5s
    const destino = proyectoId ? `/proyecto/${proyectoId}` : '/dashboard';
    setTimeout(() => {
      window.location.href = destino;
    }, 1500);
  },

  // Muestra mensaje de error en pantalla
  mostrarMensajeError(mensaje: string) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
      errorDiv.textContent = mensaje;
      errorDiv.style.display = 'block';
    }
  },
};
