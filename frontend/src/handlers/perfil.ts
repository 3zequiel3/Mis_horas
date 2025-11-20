// Gestión del perfil: datos, contraseña y configuraciones

import { AuthService } from '../services/auth';
import { AlertUtils } from '../utils/swal';
import { validateRequired, validateEmail, validatePassword, validateAll } from '../utils/validation';

export const PerfilHandler = {
  // Carga datos del usuario actual
  async loadUserData() {
    try {
      const user = await AuthService.getCurrentUser();
      const emailInput = document.getElementById('email') as HTMLInputElement;
      const usernameInput = document.getElementById('username') as HTMLInputElement;
      const nombreInput = document.getElementById('nombre_completo') as HTMLInputElement;
      const horasRealesCheckbox = document.getElementById('usar-horas-reales') as HTMLInputElement;
      const diaInicioSelect = document.getElementById('dia-inicio-semana') as HTMLSelectElement;

      if (usernameInput) usernameInput.value = user.username;
      if (emailInput) emailInput.value = user.email || '';
      if (nombreInput) nombreInput.value = user.nombre_completo || '';
      if (horasRealesCheckbox) horasRealesCheckbox.checked = user.usar_horas_reales || false;
      if (diaInicioSelect) diaInicioSelect.value = String(user.dia_inicio_semana || 0);
    } catch (error) {
      console.error('Error cargando usuario:', error);
    }
  },

  // Guarda cambios del perfil (email y nombre)
  async guardarPerfil() {
    try {
      const emailInput = document.getElementById('email') as HTMLInputElement;
      const nombreInput = document.getElementById('nombre_completo') as HTMLInputElement;

      const email = emailInput.value;
      const nombre_completo = nombreInput.value;

      // Validar email si se proporciona
      if (email) {
        const emailValidation = validateEmail(email);
        if (!emailValidation.valid) {
          await AlertUtils.error('Error', emailValidation.message!);
          return;
        }
      }

      await AuthService.updateProfile(nombre_completo, email);

      // Mostrar mensaje de éxito
      this.mostrarMensajeExito();
      await AlertUtils.success('✓ Perfil actualizado', 'Tus cambios han sido guardados');
    } catch (error) {
      console.error('Error:', error);
      this.mostrarMensajeError();
      await AlertUtils.error('Error', 'No se pudo actualizar el perfil');
    }
  },

  // Cambia la contraseña del usuario
  async cambiarContraseña() {
    try {
      const passwordActualInput = document.getElementById('password_actual') as HTMLInputElement;
      const passwordNuevaInput = document.getElementById('password_nueva') as HTMLInputElement;

      const password_actual = passwordActualInput.value;
      const password_nueva = passwordNuevaInput.value;

      // Validar campos
      const validation = validateAll(
        validateRequired(password_actual, 'Contraseña actual'),
        validateRequired(password_nueva, 'Contraseña nueva'),
        validatePassword(password_nueva, 8)
      );

      if (!validation.valid) {
        await AlertUtils.error('Error', validation.message!);
        return;
      }

      await AuthService.changePassword(password_actual, password_nueva);

      // Limpiar campos
      passwordActualInput.value = '';
      passwordNuevaInput.value = '';

      await AlertUtils.success(
        '✓ Contraseña actualizada',
        'Tu contraseña ha sido cambiada correctamente'
      );
    } catch (error) {
      console.error('Error:', error);
      await AlertUtils.error('Error', 'No se pudo cambiar la contraseña');
    }
  },

  // Actualiza configuración de horas reales y día de inicio de semana
  async actualizarConfiguracion() {
    try {
      const horasRealesCheckbox = document.getElementById('usar-horas-reales') as HTMLInputElement;
      const diaInicioSelect = document.getElementById('dia-inicio-semana') as HTMLSelectElement;
      const activar = horasRealesCheckbox.checked;
      const diaInicio = parseInt(diaInicioSelect.value);

      // Actualizar horas reales
      await AuthService.toggleHorasReales(activar);
      
      // Actualizar día de inicio de semana
      await AuthService.updateProfile(undefined, undefined, diaInicio);

      await AlertUtils.success(
        '✓ Configuración actualizada',
        'Tus preferencias han sido guardadas'
      );
      
      // Recargar la página para aplicar cambios
      setTimeout(() => window.location.reload(), 1500);
    } catch (error) {
      console.error('Error:', error);
      await AlertUtils.error('Error', 'No se pudo actualizar la configuración');
    }
  },

  // Muestra mensaje de éxito en pantalla
  mostrarMensajeExito() {
    const successMsg = document.getElementById('success-message');
    if (successMsg) {
      successMsg.style.display = 'block';
      setTimeout(() => {
        successMsg.style.display = 'none';
      }, 3000);
    }
  },

  /**
   * Muestra mensaje de error
   */
  mostrarMensajeError() {
    const errorMsg = document.getElementById('error-message');
    if (errorMsg) {
      errorMsg.style.display = 'block';
      setTimeout(() => {
        errorMsg.style.display = 'none';
      }, 3000);
    }
  },
};
