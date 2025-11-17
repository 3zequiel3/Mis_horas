export function horasAFormato(horas: number): string {
  if (!horas || horas === 0) return '00:00';
  
  const horasEnteras = Math.floor(horas);
  const minutos = Math.round((horas - horasEnteras) * 60);
  
  return `${String(horasEnteras).padStart(2, '0')}:${String(minutos).padStart(2, '0')}`;
}

export function formatoAHoras(formato: string): number {
  if (!formato || formato.trim() === '') return 0;
  
  try {
    formato = formato.trim();
    
    if (!formato.includes(':')) {
      return parseFloat(formato);
    }
    
    const [horas, minutos] = formato.split(':');
    const h = parseInt(horas, 10);
    const m = parseInt(minutos, 10) || 0;
    
    return h + m / 60;
  } catch {
    return 0;
  }
}

export const DIAS_ES = {
  0: 'Lunes',
  1: 'Martes',
  2: 'Miércoles',
  3: 'Jueves',
  4: 'Viernes',
  5: 'Sábado',
  6: 'Domingo',
};

export const MESES_ES = {
  1: 'Enero',
  2: 'Febrero',
  3: 'Marzo',
  4: 'Abril',
  5: 'Mayo',
  6: 'Junio',
  7: 'Julio',
  8: 'Agosto',
  9: 'Septiembre',
  10: 'Octubre',
  11: 'Noviembre',
  12: 'Diciembre',
};

export function formatearFecha(fecha: string | Date): string {
  const date = typeof fecha === 'string' ? new Date(fecha) : fecha;
  const dia = date.getDate();
  const mes = MESES_ES[(date.getMonth() + 1) as keyof typeof MESES_ES];
  const año = date.getFullYear();
  
  return `${dia} de ${mes} de ${año}`;
}
