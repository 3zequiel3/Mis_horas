/**
 * Utilidades para transformación y normalización de datos
 */

/**
 * Normaliza una fecha en formato YYYY-MM-DD eliminando hora si existe
 */
export function normalizarFecha(fecha: string): string {
  if (fecha.includes('T')) {
    return fecha.split('T')[0];
  } else if (fecha.includes(' ')) {
    return fecha.split(' ')[0];
  }
  return fecha;
}

/**
 * Convierte horas decimales a formato HH:MM
 * Ejemplo: 8.5 → "08:30"
 */
export function horasDecimalesAString(horas: number): string {
  const horasEnteras = Math.floor(horas);
  const minutos = Math.round((horas - horasEnteras) * 60);
  
  return `${String(horasEnteras).padStart(2, '0')}:${String(minutos).padStart(2, '0')}`;
}

/**
 * Convierte formato HH:MM a horas decimales
 * Ejemplo: "08:30" → 8.5
 */
export function stringAHorasDecimales(horasStr: string): number {
  const [horas, minutos] = horasStr.split(':').map(Number);
  return horas + minutos / 60;
}

/**
 * Formatea horas trabajadas manejando tanto string "HH:MM" como número decimal
 */
export function formatearHorasTrabajadas(horas: string | number): string {
  if (typeof horas === 'string') {
    // Si es string y contiene ":", ya está en formato correcto
    if (horas.includes(':')) {
      return horas;
    }
    // Si es string numérico, convertir a número
    const horasNum = parseFloat(horas);
    if (!isNaN(horasNum)) {
      return horasDecimalesAString(horasNum);
    }
  } else if (typeof horas === 'number') {
    return horasDecimalesAString(horas);
  }
  
  return '00:00';
}

/**
 * Capitaliza la primera letra de un string
 */
export function capitalizarPrimeraLetra(texto: string): string {
  if (!texto) return '';
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/**
 * Trunca un texto a una longitud máxima agregando "..."
 */
export function truncarTexto(texto: string, maxLength: number): string {
  if (!texto || texto.length <= maxLength) return texto;
  return texto.substring(0, maxLength) + '...';
}

/**
 * Valida si un email tiene formato válido
 */
export function esEmailValido(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

/**
 * Genera un rango de fechas entre dos fechas
 */
export function generarRangoFechas(fechaInicio: Date, fechaFin: Date): Date[] {
  const fechas: Date[] = [];
  const fecha = new Date(fechaInicio);
  
  while (fecha <= fechaFin) {
    fechas.push(new Date(fecha));
    fecha.setDate(fecha.getDate() + 1);
  }
  
  return fechas;
}

/**
 * Obtiene el inicio y fin de una semana dado un día
 * @param fecha - Fecha de referencia
 * @param diaInicio - Día de inicio de semana (0=Domingo, 1=Lunes)
 */
export function obtenerRangoSemana(fecha: Date, diaInicio: number = 1): { inicio: Date; fin: Date } {
  const dia = fecha.getDay();
  const diff = dia < diaInicio ? dia + 7 - diaInicio : dia - diaInicio;
  
  const inicio = new Date(fecha);
  inicio.setDate(fecha.getDate() - diff);
  inicio.setHours(0, 0, 0, 0);
  
  const fin = new Date(inicio);
  fin.setDate(inicio.getDate() + 6);
  fin.setHours(23, 59, 59, 999);
  
  return { inicio, fin };
}

/**
 * Formatea número a formato de moneda (AR$)
 */
export function formatearMoneda(monto: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(monto);
}

/**
 * Calcula el porcentaje de un valor sobre un total
 */
export function calcularPorcentaje(valor: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((valor / total) * 100);
}

/**
 * Agrupa un array por una propiedad específica
 */
export function agruparPor<T>(array: T[], key: keyof T): Record<string, T[]> {
  return array.reduce((grupos, item) => {
    const valor = String(item[key]);
    if (!grupos[valor]) {
      grupos[valor] = [];
    }
    grupos[valor].push(item);
    return grupos;
  }, {} as Record<string, T[]>);
}

/**
 * Elimina duplicados de un array por una propiedad
 */
export function eliminarDuplicados<T>(array: T[], key: keyof T): T[] {
  const vistos = new Set();
  return array.filter(item => {
    const valor = item[key];
    if (vistos.has(valor)) {
      return false;
    }
    vistos.add(valor);
    return true;
  });
}

/**
 * Ordena un array por una propiedad
 */
export function ordenarPor<T>(array: T[], key: keyof T, ascendente: boolean = true): T[] {
  return [...array].sort((a, b) => {
    const valorA = a[key];
    const valorB = b[key];
    
    if (valorA < valorB) return ascendente ? -1 : 1;
    if (valorA > valorB) return ascendente ? 1 : -1;
    return 0;
  });
}

/**
 * Debounce: retrasa la ejecución de una función
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * Genera un ID único simple (para uso temporal)
 */
export function generarIdTemporal(): string {
  return `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
