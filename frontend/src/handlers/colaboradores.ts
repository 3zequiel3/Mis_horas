/**
 * Handler para gestión de Colaboradores
 * Controla la vista de colaboradores en proyectos colaborativos
 */

import { ColaboradoresService, type Colaborador, type EstadisticasProyecto } from '../services/colaboradores';
import { ProyectosService } from '../services/proyectos';
import { AuthService } from '../services/auth';
import { AlertUtils } from '../utils/swal';
import type { Proyecto } from '../types';

export const ColaboradoresHandler = {
  state: {
    proyectoId: 0,
    proyecto: null as Proyecto | null,
    colaboradores: [] as Colaborador[],
    estadisticas: null as EstadisticasProyecto | null,
    esOwner: false,
  },

  /**
   * Inicializa el handler
   */
  async init(proyectoId: number): Promise<void> {
    this.state.proyectoId = proyectoId;
    
    try {
      await this.cargarProyecto();
      await this.cargarColaboradores();
      await this.cargarEstadisticas();
      this.renderizarVista();
      this.setupEventos();
    } catch (error) {
      console.error('Error inicializando colaboradores:', error);
      AlertUtils.error('Error', 'No se pudo cargar la información de colaboradores');
    }
  },

  /**
   * Carga información del proyecto
   */
  async cargarProyecto(): Promise<void> {
    this.state.proyecto = await ProyectosService.getProyecto(this.state.proyectoId);
    
    // Determinar si el usuario actual es owner
    const usuarioActual = await AuthService.getCurrentUser();
    this.state.esOwner = this.state.proyecto.usuario_id === usuarioActual.id;
  },

  /**
   * Carga la lista de colaboradores
   */
  async cargarColaboradores(): Promise<void> {
    this.state.colaboradores = await ColaboradoresService.listar(
      this.state.proyectoId,
      true // incluir estadísticas
    );
  },

  /**
   * Carga estadísticas del proyecto
   */
  async cargarEstadisticas(): Promise<void> {
    if (this.state.proyecto?.tipo_proyecto === 'colaborativo') {
      this.state.estadisticas = await ColaboradoresService.obtenerEstadisticas(this.state.proyectoId);
    }
  },

  /**
   * Renderiza la vista según el tipo de proyecto
   */
  renderizarVista(): void {
    const tipoProyecto = this.state.proyecto?.tipo_proyecto;

    // Mostrar/ocultar secciones según tipo de proyecto
    const estadoCard = document.getElementById('estado-proyecto-card');
    const btnConvertir = document.getElementById('btn-convertir-colaborativo');
    const invitarCard = document.getElementById('invitar-colaborador-card');
    const listaCard = document.getElementById('lista-colaboradores-card');
    const resumenCard = document.getElementById('resumen-colaboradores-card');

    if (tipoProyecto === 'personal') {
      // Proyecto personal: mostrar opción de convertir
      if (estadoCard) estadoCard.style.display = 'block';
      if (btnConvertir && this.state.esOwner) btnConvertir.style.display = 'block';
      if (invitarCard) invitarCard.style.display = 'none';
      if (listaCard) listaCard.style.display = 'none';
      if (resumenCard) resumenCard.style.display = 'none';
      
      const tipoTexto = document.getElementById('tipo-proyecto-text');
      if (tipoTexto) tipoTexto.textContent = 'Personal';
    } else if (tipoProyecto === 'colaborativo') {
      // Proyecto colaborativo: mostrar gestión completa
      if (estadoCard) estadoCard.style.display = 'block';
      if (btnConvertir) btnConvertir.style.display = 'none';
      if (invitarCard && this.state.esOwner) invitarCard.style.display = 'block';
      if (listaCard) listaCard.style.display = 'block';
      if (resumenCard) resumenCard.style.display = 'block';
      
      const tipoTexto = document.getElementById('tipo-proyecto-text');
      if (tipoTexto) tipoTexto.textContent = 'Colaborativo';
      
      this.renderizarColaboradores();
      this.renderizarEstadisticas();
    } else {
      // Proyecto de empleados: no aplica
      if (estadoCard) {
        estadoCard.innerHTML = `
          <h3>ℹ️ Información</h3>
          <p>Este es un proyecto de empleados. Los colaboradores solo aplican a proyectos personales o colaborativos.</p>
        `;
      }
      if (btnConvertir) btnConvertir.style.display = 'none';
      if (invitarCard) invitarCard.style.display = 'none';
      if (listaCard) listaCard.style.display = 'none';
      if (resumenCard) resumenCard.style.display = 'none';
    }
  },

  /**
   * Renderiza la lista de colaboradores
   */
  renderizarColaboradores(): void {
    const container = document.getElementById('colaboradores-list');
    if (!container) return;

    if (this.state.colaboradores.length === 0) {
      container.innerHTML = '<p class="empty-message">No hay colaboradores aún</p>';
      return;
    }

    container.innerHTML = this.state.colaboradores.map(col => `
      <div class="colaborador-item" data-usuario-id="${col.usuario_id}">
        <div class="colaborador-info">
          <div class="colaborador-header">
            <span class="colaborador-icon">${col.rol === 'owner' ? '👑' : '👤'}</span>
            <span class="colaborador-nombre">${col.usuario?.nombre_completo || col.usuario?.username || 'Usuario'}</span>
            ${col.rol === 'owner' ? '<span class="badge badge-owner">Dueño</span>' : ''}
          </div>
          <div class="colaborador-stats">
            <span class="stat-item" title="Total de horas de este colaborador en el proyecto">
              ⏱️ ${this.formatearHoras(col.estadisticas?.total_horas_trabajadas || 0)}
            </span>
            ${col.horas_reales_activas && col.estadisticas?.total_horas_reales !== undefined ? `
              <span class="stat-item" title="Total de horas reales de este colaborador">
                ✓ ${this.formatearHoras(col.estadisticas.total_horas_reales)} reales
              </span>
            ` : ''}
          </div>
          <div class="colaborador-config">
            <label class="toggle-label">
              <input 
                type="checkbox" 
                class="toggle-horas-reales" 
                data-usuario-id="${col.usuario_id}"
                ${col.horas_reales_activas ? 'checked' : ''}
                ${!this.state.esOwner || col.rol === 'owner' ? 'disabled' : ''}
              />
              <span>Horas reales</span>
            </label>
          </div>
        </div>
        ${this.state.esOwner && col.rol !== 'owner' ? `
          <div class="colaborador-actions">
            <button class="btn btn-danger btn-sm btn-eliminar-colaborador" data-usuario-id="${col.usuario_id}">
              🗑️ Eliminar
            </button>
          </div>
        ` : ''}
      </div>
    `).join('');
  },

  /**
   * Renderiza las estadísticas generales
   */
  renderizarEstadisticas(): void {
    if (!this.state.estadisticas) return;

    const totalColabs = document.getElementById('total-colaboradores');
    const totalHoras = document.getElementById('total-horas-colaboradores');

    if (totalColabs) totalColabs.textContent = this.state.estadisticas.total_colaboradores.toString();
    if (totalHoras) totalHoras.textContent = this.formatearHoras(this.state.estadisticas.total_horas_trabajadas);
  },

  /**
   * Configura los event listeners
   */
  setupEventos(): void {
    // Botón convertir a colaborativo
    const btnConvertir = document.getElementById('btn-convertir-colaborativo');
    if (btnConvertir) {
      btnConvertir.addEventListener('click', () => this.convertirAColaborativo());
    }

    // Formulario de invitación
    const formInvitar = document.getElementById('form-invitar-colaborador') as HTMLFormElement;
    if (formInvitar) {
      formInvitar.addEventListener('submit', (e) => {
        e.preventDefault();
        this.invitarColaborador();
      });
    }

    // Toggles de horas reales
    document.querySelectorAll('.toggle-horas-reales').forEach(toggle => {
      toggle.addEventListener('change', (e) => {
        const target = e.target as HTMLInputElement;
        const usuarioId = parseInt(target.dataset.usuarioId || '0');
        this.cambiarConfiguracion(usuarioId, target.checked);
      });
    });

    // Botones eliminar
    document.querySelectorAll('.btn-eliminar-colaborador').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.target as HTMLButtonElement;
        const usuarioId = parseInt(target.dataset.usuarioId || '0');
        this.eliminarColaborador(usuarioId);
      });
    });
  },

  /**
   * Convierte el proyecto a colaborativo
   */
  async convertirAColaborativo(): Promise<void> {
    const result = await AlertUtils.confirm(
      '¿Convertir a colaborativo?',
      'Podrás invitar a otros usuarios a trabajar en este proyecto'
    );

    if (!result) return;

    try {
      AlertUtils.loading('Convirtiendo proyecto...');
      await ColaboradoresService.convertirAColaborativo(this.state.proyectoId);
      
      await this.init(this.state.proyectoId); // Recargar todo
      
      AlertUtils.close();
      await AlertUtils.success('¡Éxito!', 'Proyecto convertido a colaborativo');
    } catch (error: any) {
      AlertUtils.close();
      await AlertUtils.error('Error', error.message || 'No se pudo convertir el proyecto');
    }
  },

  /**
   * Invita a un nuevo colaborador
   */
  async invitarColaborador(): Promise<void> {
    const emailInput = document.getElementById('email-colaborador') as HTMLInputElement;
    const horasRealesCheck = document.getElementById('horas-reales-colaborador') as HTMLInputElement;

    if (!emailInput || !emailInput.value.trim()) {
      await AlertUtils.error('Error', 'Debes ingresar un email');
      return;
    }

    try {
      AlertUtils.loading('Enviando invitación...');
      
      await ColaboradoresService.invitar(
        this.state.proyectoId,
        emailInput.value.trim(),
        horasRealesCheck?.checked || false
      );

      emailInput.value = '';
      if (horasRealesCheck) horasRealesCheck.checked = false;

      await this.cargarColaboradores();
      await this.cargarEstadisticas();
      this.renderizarColaboradores();
      this.renderizarEstadisticas();
      this.setupEventos();

      AlertUtils.close();
      await AlertUtils.success('¡Invitado!', 'Colaborador agregado al proyecto');
    } catch (error: any) {
      AlertUtils.close();
      await AlertUtils.error('Error', error.message || 'No se pudo enviar la invitación');
    }
  },

  /**
   * Cambia la configuración de un colaborador
   */
  async cambiarConfiguracion(usuarioId: number, horasRealesActivas: boolean): Promise<void> {
    try {
      await ColaboradoresService.actualizarConfiguracion(
        this.state.proyectoId,
        usuarioId,
        horasRealesActivas
      );

      await this.cargarColaboradores();
      this.renderizarColaboradores();
      this.setupEventos();
    } catch (error: any) {
      await AlertUtils.error('Error', error.message || 'No se pudo actualizar la configuración');
    }
  },

  /**
   * Elimina un colaborador
   */
  async eliminarColaborador(usuarioId: number): Promise<void> {
    const result = await AlertUtils.confirm(
      '¿Eliminar colaborador?',
      'Este usuario ya no tendrá acceso al proyecto'
    );

    if (!result) return;

    try {
      AlertUtils.loading('Eliminando...');
      
      await ColaboradoresService.eliminar(this.state.proyectoId, usuarioId);

      await this.cargarColaboradores();
      await this.cargarEstadisticas();
      this.renderizarColaboradores();
      this.renderizarEstadisticas();
      this.setupEventos();

      AlertUtils.close();
      await AlertUtils.success('Eliminado', 'Colaborador eliminado del proyecto');
    } catch (error: any) {
      AlertUtils.close();
      await AlertUtils.error('Error', error.message || 'No se pudo eliminar el colaborador');
    }
  },

  /**
   * Formatea horas a formato HH:MM
   */
  formatearHoras(horas: number): string {
    const h = Math.floor(horas);
    const m = Math.round((horas - h) * 60);
    return `${h}:${m.toString().padStart(2, '0')}`;
  },
};
