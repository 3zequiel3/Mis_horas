/**
 * Handler para el Drawer de Configuración de Proyectos
 * Gestiona la apertura, edición y guardado de configuración
 */


import { ProyectosService } from "../services/proyectos";
import { AlertUtils } from "../utils/swal";
import type { Proyecto, ModulesConfig } from "../types";

export class ConfigDrawerHandler {
  private proyectoId: number;
  private drawer: HTMLElement | null = null;
  private overlay: HTMLElement | null = null;
  private proyecto: Proyecto | null = null;

  constructor(proyectoId: number) {
    this.proyectoId = proyectoId;
  }

  /**
   * Abre el drawer y carga la configuración actual
   */
  async open(): Promise<void> {
    try {
      this.drawer = document.getElementById("config-drawer");
      this.overlay = document.getElementById("drawer-overlay");

      if (!this.drawer) {
        AlertUtils.error("Error", "No se encontró el componente del drawer");
        return;
      }

      this.proyecto = await ProyectosService.getProyecto(this.proyectoId);

      this.loadGeneralData();
      this.loadModulesData();
      this.loadBudgetData();
      this.loadTimeData();

      this.setupEventListeners();

      this.drawer.classList.add("active");
      document.body.style.overflow = "hidden";
    } catch (error: any) {
      console.error("Error al abrir configuración:", error);
      AlertUtils.error(
        "Error al cargar configuración",
        error.message || "No se pudo cargar la configuración del proyecto"
      );
    }
  }

  close(): void {
    if (this.drawer) {
      this.drawer.classList.remove("active");
      document.body.style.overflow = "";
      this.cleanup();
    }
  }

  private loadGeneralData(): void {
    if (!this.proyecto) return;

    const clientNameInput = document.getElementById("client_name") as HTMLInputElement;
    const brandColorInput = document.getElementById("brand_color") as HTMLInputElement;
    const brandColorPicker = document.getElementById("brand_color_picker") as HTMLInputElement;

    if (clientNameInput) clientNameInput.value = this.proyecto.client_name || "";
    if (brandColorInput) brandColorInput.value = this.proyecto.brand_color || "#3B82F6";
    if (brandColorPicker) brandColorPicker.value = this.proyecto.brand_color || "#3B82F6";

    if (this.proyecto.brand_color) {
      const preset = document.querySelector(
        `.color-preset[data-color="${this.proyecto.brand_color}"]`
      );
      if (preset) {
        document.querySelectorAll(".color-preset").forEach((p) => p.classList.remove("selected"));
        preset.classList.add("selected");
      }
    }
  }

  private loadModulesData(): void {
    if (!this.proyecto) return;

    const modulesConfig: ModulesConfig = this.proyecto.modules_config || {
      time_tracking: true,
      budget: false,
      audit: false,
      approvals: false,
      public_view: false,
    };

    Object.entries(modulesConfig).forEach(([module, enabled]) => {
      const checkbox = document.querySelector(
        `.module-toggle[data-module="${module}"]`
      ) as HTMLInputElement;
      if (checkbox) checkbox.checked = enabled as boolean;
    });
  }

  private loadBudgetData(): void {
    if (!this.proyecto) return;

          const budgetTypeSelect = document.getElementById("budget_type") as HTMLSelectElement;
          const budgetAmountInput = document.getElementById("budget_base_amount") as HTMLInputElement;
          const currencySelect = document.getElementById("currency") as HTMLSelectElement;

          if (budgetTypeSelect) budgetTypeSelect.value = this.proyecto.budget_type || "none";
          if (budgetAmountInput) budgetAmountInput.value = String(this.proyecto.budget_base_amount || "");
          if (currencySelect) currencySelect.value = this.proyecto.currency || "USD";

          this.toggleBudgetAmountSection(this.proyecto.budget_type);
        }

        private loadTimeData(): void {
          if (!this.proyecto) return;

          const horasRealesCheck = document.getElementById("horas_reales_activas") as HTMLInputElement;
          const modoHorariosSelect = document.getElementById("modo_horarios") as HTMLSelectElement;

          if (horasRealesCheck) horasRealesCheck.checked = this.proyecto.horas_reales_activas || false;
          if (modoHorariosSelect) modoHorariosSelect.value = this.proyecto.modo_horarios || "";

          const inicioInput = document.getElementById("horario_inicio") as HTMLInputElement;
          const finInput = document.getElementById("horario_fin") as HTMLInputElement;
          const mananaInicio = document.getElementById("turno_manana_inicio") as HTMLInputElement;
          const mananaFin = document.getElementById("turno_manana_fin") as HTMLInputElement;
          const tardeInicio = document.getElementById("turno_tarde_inicio") as HTMLInputElement;
          const tardeFin = document.getElementById("turno_tarde_fin") as HTMLInputElement;

          if (inicioInput) inicioInput.value = this.proyecto.horario_inicio || "";
          if (finInput) finInput.value = this.proyecto.horario_fin || "";
          if (mananaInicio) mananaInicio.value = this.proyecto.turno_manana_inicio || "";
          if (mananaFin) mananaFin.value = this.proyecto.turno_manana_fin || "";
          if (tardeInicio) tardeInicio.value = this.proyecto.turno_tarde_inicio || "";
          if (tardeFin) tardeFin.value = this.proyecto.turno_tarde_fin || "";

          this.toggleTimeConfigSection(this.proyecto.modo_horarios);
        }

        private setupEventListeners(): void {
          const closeBtn = document.getElementById("drawer-close");
          if (closeBtn) closeBtn.addEventListener("click", () => this.close());

          if (this.overlay) this.overlay.addEventListener("click", () => this.close());

          const tabs = document.querySelectorAll(".drawer-tab");
          tabs.forEach((tab) => {
            tab.addEventListener("click", (e) => {
              const target = e.target as HTMLElement;
              const tabName = target.dataset.tab;
              if (tabName) this.switchTab(tabName);
            });
          });

          this.setupColorPicker();

          const budgetTypeSelect = document.getElementById("budget_type");
          if (budgetTypeSelect) {
            budgetTypeSelect.addEventListener("change", (e) => {
              const select = e.target as HTMLSelectElement;
              this.toggleBudgetAmountSection(select.value);
            });
          }

          const modoHorariosSelect = document.getElementById("modo_horarios");
          if (modoHorariosSelect) {
            modoHorariosSelect.addEventListener("change", (e) => {
              const select = e.target as HTMLSelectElement;
              this.toggleTimeConfigSection(select.value);
            });
          }

          const formGeneral = document.getElementById("form-general");
          if (formGeneral) {
            formGeneral.addEventListener("submit", (e) => {
              e.preventDefault();
              this.saveGeneral();
            });
          }

          const btnSaveModules = document.getElementById("btn-save-modules");
          if (btnSaveModules) btnSaveModules.addEventListener("click", () => this.saveModules());

          const formBudget = document.getElementById("form-budget");
          if (formBudget) {
            formBudget.addEventListener("submit", (e) => {
              e.preventDefault();
              this.saveBudget();
            });
          }

          const formTime = document.getElementById("form-time");
          if (formTime) {
            formTime.addEventListener("submit", (e) => {
              e.preventDefault();
              this.saveTime();
            });
          }
        }

        private setupColorPicker(): void {
          const colorPresets = document.querySelectorAll(".color-preset");
          const colorInput = document.getElementById("brand_color") as HTMLInputElement;
          const colorPicker = document.getElementById("brand_color_picker") as HTMLInputElement;

          colorPresets.forEach((preset) => {
            preset.addEventListener("click", () => {
              const color = (preset as HTMLElement).dataset.color;
              if (color) {
                colorPresets.forEach((p) => p.classList.remove("selected"));
                preset.classList.add("selected");
                if (colorInput) colorInput.value = color;
                if (colorPicker) colorPicker.value = color;
              }
            });
          });

          if (colorPicker) {
            colorPicker.addEventListener("input", (e) => {
              const value = (e.target as HTMLInputElement).value;
              if (colorInput) colorInput.value = value;
              colorPresets.forEach((p) => p.classList.remove("selected"));
            });
          }

          if (colorInput) {
            colorInput.addEventListener("input", (e) => {
              const value = (e.target as HTMLInputElement).value;
              if (colorPicker && /^#[0-9A-F]{6}$/i.test(value)) {
                colorPicker.value = value;
              }
              colorPresets.forEach((p) => p.classList.remove("selected"));
            });
          }
        }

        private switchTab(tabName: string): void {
          document.querySelectorAll(".drawer-tab").forEach((tab) => tab.classList.remove("active"));
          document.querySelector(`.drawer-tab[data-tab="${tabName}"]`)?.classList.add("active");

          document.querySelectorAll(".drawer-tab-content").forEach((content) => content.classList.remove("active"));
          document.querySelector(`.drawer-tab-content[data-tab="${tabName}"]`)?.classList.add("active");
        }

        private toggleBudgetAmountSection(budgetType: string | undefined): void {
          const amountSection = document.getElementById("budget-amount-section");
          const amountLabel = document.getElementById("budget-amount-label");

          if (!amountSection) return;

          if (budgetType && budgetType !== "none") {
            amountSection.style.display = "block";
            if (amountLabel) {
              switch (budgetType) {
                case "hourly_retainer":
                  amountLabel.textContent = "Horas del retainer";
                  break;
                case "time_and_materials":
                  amountLabel.textContent = "Tarifa por hora";
                  break;
                default:
                  amountLabel.textContent = "Monto";
              }
            }
          } else {
            amountSection.style.display = "none";
          }
        }

        private toggleTimeConfigSection(modo: string | undefined): void {
          const configCorrido = document.getElementById("config-corrido");
          const configTurnos = document.getElementById("config-turnos");

          if (configCorrido) configCorrido.style.display = modo === "corrido" ? "block" : "none";
          if (configTurnos) configTurnos.style.display = modo === "turnos" ? "block" : "none";
        }

        private async saveGeneral(): Promise<void> {
          try {
            const clientNameInput = document.getElementById("client_name") as HTMLInputElement;
            const brandColorInput = document.getElementById("brand_color") as HTMLInputElement;

            const data = {
              client_name: clientNameInput?.value || null,
              brand_color: brandColorInput?.value || "#3B82F6",
            };

            await ProyectosService.updateProyecto(this.proyectoId, data);

            AlertUtils.success("✅ Guardado", "Configuración general actualizada");

            if (this.proyecto) {
              this.proyecto.client_name = data.client_name;
              this.proyecto.brand_color = data.brand_color;
            }

            setTimeout(() => window.location.reload(), 800);
          } catch (error: any) {
            console.error("Error al guardar general:", error);
            AlertUtils.error("Error", error.message || "No se pudo guardar la configuración");
          }
        }

        private async saveModules(): Promise<void> {
          try {
            const modulesConfig: ModulesConfig = {
              time_tracking: (document.querySelector('.module-toggle[data-module="time_tracking"]') as HTMLInputElement)?.checked || false,
              budget: (document.querySelector('.module-toggle[data-module="budget"]') as HTMLInputElement)?.checked || false,
              audit: (document.querySelector('.module-toggle[data-module="audit"]') as HTMLInputElement)?.checked || false,
              approvals: (document.querySelector('.module-toggle[data-module="approvals"]') as HTMLInputElement)?.checked || false,
              public_view: (document.querySelector('.module-toggle[data-module="public_view"]') as HTMLInputElement)?.checked || false,
            };

            await ProyectosService.updateProyecto(this.proyectoId, { modules_config: modulesConfig });

            if (this.proyecto) this.proyecto.modules_config = modulesConfig;
            if ((window as any).updateSidebarModules) (window as any).updateSidebarModules(modulesConfig);

            await AlertUtils.success("✅ Guardado", "Módulos actualizados correctamente");
            window.location.reload();
          } catch (error: any) {
            console.error("Error al guardar módulos:", error);
            AlertUtils.error("Error", error.message || "No se pudo guardar los módulos");
          }
        }

        private async saveBudget(): Promise<void> {
          try {
            const budgetTypeSelect = document.getElementById("budget_type") as HTMLSelectElement;
            const budgetAmountInput = document.getElementById("budget_base_amount") as HTMLInputElement;
            const currencySelect = document.getElementById("currency") as HTMLSelectElement;

            const budgetType = (budgetTypeSelect?.value || "none") as "none" | "hourly_retainer" | "time_and_materials" | "fixed_price";
            const amount = budgetType !== "none" ? parseFloat(budgetAmountInput?.value || "0") : null;

            const data = {
              budget_type: budgetType,
              budget_base_amount: amount,
              currency: currencySelect?.value || "USD",
            };

            await ProyectosService.updateProyecto(this.proyectoId, data);

            AlertUtils.success("✅ Guardado", "Presupuesto actualizado correctamente");

            if (this.proyecto) {
              this.proyecto.budget_type = data.budget_type;
              this.proyecto.budget_base_amount = data.budget_base_amount;
              this.proyecto.currency = data.currency;
            }
          } catch (error: any) {
            console.error("Error al guardar presupuesto:", error);
            AlertUtils.error("Error", error.message || "No se pudo guardar el presupuesto");
          }
        }

        private async saveTime(): Promise<void> {
          try {
            const horasRealesCheck = document.getElementById("horas_reales_activas") as HTMLInputElement;
            const modoHorariosSelect = document.getElementById("modo_horarios") as HTMLSelectElement;

            const modo = modoHorariosSelect?.value || "";
            const data: any = {
              horas_reales_activas: horasRealesCheck?.checked || false,
              modo_horarios: modo || null,
            };

            if (modo === "corrido") {
              const inicioInput = document.getElementById("horario_inicio") as HTMLInputElement;
              const finInput = document.getElementById("horario_fin") as HTMLInputElement;
              data.horario_inicio = inicioInput?.value || null;
              data.horario_fin = finInput?.value || null;
            } else if (modo === "turnos") {
              const mananaInicio = document.getElementById("turno_manana_inicio") as HTMLInputElement;
              const mananaFin = document.getElementById("turno_manana_fin") as HTMLInputElement;
              const tardeInicio = document.getElementById("turno_tarde_inicio") as HTMLInputElement;
              const tardeFin = document.getElementById("turno_tarde_fin") as HTMLInputElement;

              data.turno_manana_inicio = mananaInicio?.value || null;
              data.turno_manana_fin = mananaFin?.value || null;
              data.turno_tarde_inicio = tardeInicio?.value || null;
              data.turno_tarde_fin = tardeFin?.value || null;
            }

            await ProyectosService.updateConfiguracion(this.proyectoId, data);

            AlertUtils.success("✅ Guardado", "Configuración de horarios actualizada");

            if (this.proyecto) {
              this.proyecto.horas_reales_activas = data.horas_reales_activas;
              this.proyecto.modo_horarios = data.modo_horarios;
              if (data.horario_inicio !== undefined) this.proyecto.horario_inicio = data.horario_inicio;
              if (data.horario_fin !== undefined) this.proyecto.horario_fin = data.horario_fin;
              if (data.turno_manana_inicio !== undefined) this.proyecto.turno_manana_inicio = data.turno_manana_inicio;
              if (data.turno_manana_fin !== undefined) this.proyecto.turno_manana_fin = data.turno_manana_fin;
              if (data.turno_tarde_inicio !== undefined) this.proyecto.turno_tarde_inicio = data.turno_tarde_inicio;
              if (data.turno_tarde_fin !== undefined) this.proyecto.turno_tarde_fin = data.turno_tarde_fin;
            }

            setTimeout(() => window.location.reload(), 800);
          } catch (error: any) {
            console.error("Error al guardar horarios:", error);
            AlertUtils.error("Error", error.message || "No se pudo guardar la configuración de horarios");
          }
        }

        private cleanup(): void {
          this.drawer = null;
          this.overlay = null;
        }
}
