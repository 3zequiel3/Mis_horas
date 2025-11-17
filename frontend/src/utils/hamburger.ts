/**
 * Utility para gestionar el menú hamburguesa en dispositivos móviles
 */

export class HamburgerMenu {
  private menuToggle: HTMLElement | null;
  private navMenu: HTMLElement | null;
  private isOpen: boolean = false;

  constructor(toggleSelector: string, menuSelector: string) {
    this.menuToggle = document.querySelector(toggleSelector);
    this.navMenu = document.querySelector(menuSelector);
    this.init();
  }

  private init(): void {
    if (!this.menuToggle || !this.navMenu) {
      console.warn('Hamburger menu elements not found');
      return;
    }

    // Event listener para el botón hamburguesa
    this.menuToggle.addEventListener('click', () => this.toggle());

    // Cerrar menú al hacer clic en un enlace
    const links = this.navMenu.querySelectorAll('.nav-link, button');
    links.forEach(link => {
      link.addEventListener('click', () => {
        if (this.isOpen && window.innerWidth <= 768) {
          this.close();
        }
      });
    });

    // Cerrar menú al hacer clic fuera
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      if (this.isOpen && 
          !this.navMenu?.contains(target) && 
          !this.menuToggle?.contains(target) &&
          window.innerWidth <= 768) {
        this.close();
      }
    });

    // Cerrar menú al cambiar tamaño de ventana
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768 && this.isOpen) {
        this.close();
      }
    });
  }

  private toggle(): void {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  private open(): void {
    if (!this.navMenu || !this.menuToggle) return;
    
    this.navMenu.classList.add('active');
    this.menuToggle.classList.add('active');
    this.isOpen = true;
    
    // Prevenir scroll del body cuando el menú está abierto
    document.body.style.overflow = 'hidden';
  }

  private close(): void {
    if (!this.navMenu || !this.menuToggle) return;
    
    this.navMenu.classList.remove('active');
    this.menuToggle.classList.remove('active');
    this.isOpen = false;
    
    // Restaurar scroll del body
    document.body.style.overflow = '';
  }

  public destroy(): void {
    // Cleanup si es necesario
    this.close();
  }
}

/**
 * Inicializa el menú hamburguesa
 */
export function initHamburgerMenu(): void {
  if (typeof window !== 'undefined') {
    new HamburgerMenu('.hamburger-toggle', '.nav-menu');
  }
}
