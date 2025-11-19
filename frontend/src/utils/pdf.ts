/**
 * Utilidades para generar PDFs - Modular y escalable
 * Soporta generación de tablas, títulos y contenido personalizado
 */

import jsPDF from 'jspdf';
import type { Tarea, Dia } from '../types';
import { horasAFormato } from './formatters';

/**
 * Opciones base para configurar PDFs
 */
export interface PDFOptions {
  title: string;
  fileName: string;
  orientation?: 'portrait' | 'landscape';
  fontSize?: number;
  margin?: number;
}

/**
 * Configuración de tabla en PDF
 */
export interface TableConfig {
  headers: string[];
  rows: (string | number)[][];
  columnWidths?: number[];
  rowHeight?: number;
}



/**
 * Genera PDF desde una plantilla usando drawTable mejorado
 * Sin html2canvas - genera directamente con jsPDF para mejor control
 */
export async function generatePDFFromTemplate(
  projectName: string,
  month: string,
  year: number,
  tareas: Tarea[],
  dias: Dia[]
): Promise<void> {
  try {
    // Preparar datos de tareas con días asociados
    const tareasConDias = tareas.map((tarea) => {
      const diasTarea = tarea.dias || [];
      const diasAsociados = diasTarea.length > 0
        ? diasTarea.map((d) => new Date(d.fecha).getDate()).join(', ')
        : '-';

      return {
        titulo: tarea.titulo || '-',
        detalle: tarea.detalle || '-',
        horas: tarea.horas || '00:00',
        diasAsociados,
      };
    });

    // Calcular total de horas
    const totalHoras = tareasConDias.reduce((sum, t) => {
      const [horas, minutos] = t.horas.split(':').map(Number);
      return sum + (horas || 0) + (minutos || 0) / 60;
    }, 0);
    const horasTotal = Math.floor(totalHoras);
    const minutosTotal = Math.round((totalHoras - horasTotal) * 60);
    const totalFormateado = `${horasTotal}:${minutosTotal.toString().padStart(2, '0')}`;

    // Crear PDF
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 20;
    let currentY = margin;

    // Fondo oscuro completo
    pdf.setFillColor(17, 21, 29); // #11151D
    pdf.rect(0, 0, pageWidth, pageHeight, 'F');

    // Título
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(217, 217, 217); // #D9D9D9
    pdf.text(projectName, margin, currentY);
    currentY += 8;

    // Subtítulo (mes y año)
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(156, 163, 175); // #9CA3AF
    pdf.text(`${month} ${year}`, margin, currentY);
    currentY += 10;

    // Preparar datos para la tabla
    const headers = ['Tarea', 'Detalle', 'Horas', 'Días'];
    const rows = tareasConDias.map((t) => [t.titulo, t.detalle, t.horas, t.diasAsociados]);

    // Configuración de columnas - dar más espacio a Detalle
    const tableWidth = pageWidth - (2 * margin);
    const columnWidths = [
      tableWidth * 0.20,  // Tarea: 20%
      tableWidth * 0.40,  // Detalle: 40% (más espacio)
      tableWidth * 0.20,  // Horas: 20%
      tableWidth * 0.20,  // Días: 20%
    ];

    // Dibujar tabla con manejo de páginas
    currentY = drawTableWithPagination(pdf, {
      headers,
      rows,
      columnWidths,
    }, margin, currentY);

    // Dibujar fila de Total con celdas combinadas y estilo verde "Activo"
    const totalHeight = 10;

    // Verificar si cabe en la página actual
    if (currentY + totalHeight > pageHeight - margin) {
      pdf.addPage();
      pdf.setFillColor(17, 21, 29); // #11151D
      pdf.rect(0, 0, pageWidth, pageHeight, 'F');
      currentY = margin;
    }

    // Primera celda combinada: "Total" (Tarea + Detalle)
    const totalLabelWidth = columnWidths[0] + columnWidths[1];
    pdf.setFillColor(5, 46, 22); // Verde oscuro estilo "Activo"
    pdf.rect(margin, currentY, totalLabelWidth, totalHeight, 'F');
    pdf.setDrawColor(34, 197, 94); // Verde claro para borde
    pdf.setLineWidth(0.5);
    pdf.rect(margin, currentY, totalLabelWidth, totalHeight);

    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(8);
    pdf.setTextColor(34, 197, 94); // Verde claro #22C55E
    pdf.text('Total', margin + totalLabelWidth / 2, currentY + totalHeight / 2 + 1.5, {
      align: 'center',
    });

    // Segunda celda combinada: Valor del total (Horas + Días)
    const totalValueWidth = columnWidths[2] + columnWidths[3];
    const totalValueX = margin + totalLabelWidth;
    pdf.setFillColor(5, 46, 22); // Verde oscuro estilo "Activo"
    pdf.rect(totalValueX, currentY, totalValueWidth, totalHeight, 'F');
    pdf.setDrawColor(34, 197, 94); // Verde claro para borde
    pdf.rect(totalValueX, currentY, totalValueWidth, totalHeight);

    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(34, 197, 94); // Verde claro
    pdf.text(totalFormateado, totalValueX + totalValueWidth / 2, currentY + totalHeight / 2 + 1.5, {
      align: 'center',
    });

    // Guardar el PDF
    pdf.save(`${projectName}-${month}-${year}.pdf`);
  } catch (error) {
    console.error('Error generando PDF desde plantilla:', error);
    throw error;
  }
}

/**
 * Dibuja tabla con paginación automática y fondo oscuro consistente
 */
function drawTableWithPagination(
  pdf: jsPDF,
  config: TableConfig,
  startX: number,
  startY: number
): number {
  const headers = config.headers;
  const rows = config.rows;
  const columnWidths = config.columnWidths || [];

  const fontSize = 8;
  const headerFontSize = 9;
  const lineHeight = 3.5;
  const cellPadding = 4;
  const minRowHeight = 8;
  const maxRowHeight = 150; // Límite máximo para una fila

  let currentY = startY;
  const pageHeight = pdf.internal.pageSize.getHeight();
  const pageWidth = pdf.internal.pageSize.getWidth();
  const margin = 20;
  const pageBottom = pageHeight - margin;

  // Función para dibujar el header
  const drawHeader = (y: number) => {
    pdf.setFontSize(headerFontSize);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(217, 217, 217);
    pdf.setDrawColor(218, 218, 218);
    pdf.setLineWidth(0.5);

    const headerHeight = 10;
    for (let i = 0; i < headers.length; i++) {
      const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);

      pdf.setFillColor(26, 26, 46); // #1A1A2E
      pdf.rect(x, y, columnWidths[i], headerHeight, 'FD');

      pdf.text(headers[i], x + columnWidths[i] / 2, y + headerHeight / 2 + 1.5, {
        align: 'center',
      });
    }

    return y + headerHeight;
  };

  // Dibujar header inicial
  currentY = drawHeader(currentY);

  // Dibujar filas
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(fontSize);

  rows.forEach((row, rowIndex) => {
    // Calcular altura real necesaria
    let calculatedHeight = minRowHeight;

    for (let i = 0; i < row.length; i++) {
      const cellValue = String(row[i] || '-');
      const cellWidth = columnWidths[i] - (cellPadding * 2);
      const lines = pdf.splitTextToSize(cellValue, cellWidth);
      const cellHeight = (lines.length * lineHeight) + (cellPadding * 2);

      if (cellHeight > calculatedHeight) {
        calculatedHeight = cellHeight;
      }
    }

    // Limitar la altura máxima
    const finalHeight = Math.min(calculatedHeight, maxRowHeight);

    // Verificar si cabe en la página actual
    if (currentY + finalHeight > pageBottom) {
      // Nueva página
      pdf.addPage();
      pdf.setFillColor(17, 21, 29); // #11151D
      pdf.rect(0, 0, pageWidth, pageHeight, 'F');

      currentY = margin;
      currentY = drawHeader(currentY);

      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(fontSize);
    }

    // Dibujar celdas de la fila
    for (let i = 0; i < row.length; i++) {
      const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);

      // Fondo de tabla
      pdf.setFillColor(26, 26, 46); // #1A1A2E
      pdf.rect(x, currentY, columnWidths[i], finalHeight, 'F');

      // Borde
      pdf.setDrawColor(218, 218, 218);
      pdf.setLineWidth(0.5);
      pdf.rect(x, currentY, columnWidths[i], finalHeight);

      // Contenido
      const cellValue = String(row[i] || '-');
      const cellWidth = columnWidths[i] - (cellPadding * 2);
      const lines = pdf.splitTextToSize(cellValue, cellWidth);

      // Limitar número de líneas si es muy largo
      const maxLines = Math.floor((finalHeight - (cellPadding * 2)) / lineHeight);
      const visibleLines = lines.slice(0, maxLines);

      // Estilo de texto
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(217, 217, 217);

      // Calcular posición Y inicial del texto
      const totalTextHeight = visibleLines.length * lineHeight;
      const startTextY = currentY + (finalHeight - totalTextHeight) / 2 + (lineHeight / 2);

      // Alineación: columna Detalle (índice 1) a la izquierda, el resto centradas
      const align = i === 1 ? 'left' : 'center';
      const textX = align === 'center' ? x + columnWidths[i] / 2 : x + cellPadding;

      // Dibujar líneas de texto
      visibleLines.forEach((line: string, lineIndex: number) => {
        const textY = startTextY + (lineIndex * lineHeight);
        pdf.text(line, textX, textY, {
          align: align as 'left' | 'center',
          maxWidth: cellWidth,
        });
      });
    }

    currentY += finalHeight;
  });

  return currentY;
}



/**
 * Genera PDF de empleado con horarios de entrada/salida
 * Formato: Nombre | Día | Entrada | Salida | Horas trabajadas | Total dentro de la tabla
 * Usa los mismos estilos que generateTasksPDF con colores en filas según horas
 */
export async function generateEmpleadoPDF(
  empleadoNombre: string,
  proyectoNombre: string,
  periodo: string,
  dias: Dia[]
): Promise<void> {
  try {
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 20;
    let currentY = margin;

    // Fondo oscuro completo
    pdf.setFillColor(17, 21, 29); // #11151D
    pdf.rect(0, 0, pageWidth, pageHeight, 'F');

    // Título
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(217, 217, 217); // #D9D9D9
    pdf.text(empleadoNombre, margin, currentY);
    currentY += 8;

    // Subtítulo (proyecto y período)
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(156, 163, 175); // #9CA3AF
    pdf.text(`${proyectoNombre} - ${periodo}`, margin, currentY);
    currentY += 10;

    // ==================== TABLA CON COLORES POR FILA ====================
    if (dias.length === 0) {
      pdf.setFontSize(12);
      pdf.setTextColor(180, 180, 180);
      pdf.text('No hay registros para mostrar', margin, currentY);
    } else {
      // Calcular total de horas ANTES de crear la tabla
      let totalHorasNum = 0;
      dias.forEach((dia) => {
        totalHorasNum += dia.horas_trabajadas || 0;
      });
      const totalFormato = horasAFormato(totalHorasNum);

      // Crear tabla con drawTableEmpleado (versión personalizada con colores)
      currentY = drawTableEmpleado(pdf, dias, margin, currentY, totalFormato, dias.length);
    }

    // ==================== FOOTER ====================
    const pageCount = pdf.getNumberOfPages();
    pdf.setFontSize(8);
    pdf.setTextColor(107, 114, 128); // gray-500
    pdf.setFont('helvetica', 'normal');

    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);

      // Línea divisoria
      pdf.setDrawColor(55, 65, 81); // gray-700
      pdf.setLineWidth(0.3);
      pdf.line(margin, pageHeight - 10, pageWidth - margin, pageHeight - 10);

      // Número de página
      pdf.setTextColor(107, 114, 128);
      pdf.text(
        `Página ${i} de ${pageCount}`,
        pageWidth - margin - 20,
        pageHeight - 6
      );
    }

    // Descargar
    const fileName = `${empleadoNombre.replace(/\s/g, '_')}-${periodo.replace(/\s/g, '_')}.pdf`;
    pdf.save(fileName);
  } catch (error) {
    console.error('Error generando PDF de empleado:', error);
    throw error;
  }
}

/**
 * Dibuja tabla de empleado con colores en filas según horas trabajadas
 * Verde tenue si tiene horas, rojo tenue si no tiene
 */
function drawTableEmpleado(
  pdf: jsPDF,
  dias: Dia[],
  startX: number,
  startY: number,
  totalFormato: string,
  totalDias: number
): number {
  const headers = ['Día', 'Fecha', 'Entrada', 'Salida', 'Horas Trabajadas'];

  // Calcular ancho disponible
  const pageWidth = pdf.internal.pageSize.getWidth();
  const totalAvailableWidth = pageWidth - 40; // 20mm margen a cada lado

  // Distribuir ancho equitativamente
  const columnWidths = Array(headers.length).fill(totalAvailableWidth / headers.length);

  const fontSize = 8;
  const headerFontSize = 9;
  const minRowHeight = 8;

  let currentY = startY;
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 20;
  const pageBottom = pageHeight - margin;

  // ========== DIBUJAR HEADERS ==========
  // Headers con estilo oscuro - igual que tabla de tareas
  pdf.setFontSize(headerFontSize);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(217, 217, 217);
  pdf.setDrawColor(218, 218, 218);
  pdf.setLineWidth(0.5);

  const headerHeight = 10;
  for (let i = 0; i < headers.length; i++) {
    const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);

    pdf.setFillColor(26, 26, 46); // #1A1A2E - fondo oscuro
    pdf.rect(x, currentY, columnWidths[i], headerHeight, 'FD');

    pdf.text(headers[i], x + columnWidths[i] / 2, currentY + headerHeight / 2 + 1.5, {
      align: 'center',
    });
  }

  currentY += headerHeight;

  // ========== DIBUJAR FILAS CON COLORES ===========
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(fontSize);
  pdf.setLineWidth(0.2);

  dias.forEach((dia, rowIndex) => {
    const fecha = new Date(dia.fecha);
    const fechaStr = fecha.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit'
    });
    const horaEntrada = dia.hora_entrada || '--:--';
    const horaSalida = dia.hora_salida || '--:--';
    const horasTrabajadas = dia.horas_trabajadas
      ? horasAFormato(dia.horas_trabajadas)
      : '--:--';

    const row = [
      dia.dia_semana || '-',
      fechaStr,
      horaEntrada,
      horaSalida,
      horasTrabajadas,
    ];

    // Calcular altura de fila
    let maxRowHeight = minRowHeight;
    for (let i = 0; i < row.length; i++) {
      const cellValue = String(row[i] || '-');
      const cellWidth = columnWidths[i] - 5;
      const lines = pdf.splitTextToSize(cellValue, cellWidth);
      const cellHeight = lines.length * 6 + 6;
      if (cellHeight > maxRowHeight) {
        maxRowHeight = cellHeight;
      }
    }

    if (maxRowHeight < minRowHeight) {
      maxRowHeight = minRowHeight;
    }

    // Verificar si necesita nueva página
    if (currentY + maxRowHeight > pageBottom) {
      pdf.addPage();
      pdf.setFillColor(17, 21, 29); // #11151D
      pdf.rect(0, 0, pageWidth, pageHeight, 'F');
      currentY = margin;

      // Redibujar header con estilo oscuro
      pdf.setFontSize(headerFontSize);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(217, 217, 217);
      pdf.setDrawColor(218, 218, 218);
      pdf.setLineWidth(0.5);

      for (let i = 0; i < headers.length; i++) {
        const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);
        pdf.setFillColor(26, 26, 46); // #1A1A2E
        pdf.rect(x, currentY, columnWidths[i], headerHeight, 'FD');
        pdf.text(headers[i], x + columnWidths[i] / 2, currentY + headerHeight / 2 + 1.5, {
          align: 'center',
        });
      }

      currentY += headerHeight;
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(fontSize);
      pdf.setLineWidth(0.2);
    }

    // COLOR DE FONDO SEGÚN HORAS TRABAJADAS (colores más tenues)
    const tieneHoras = dia.horas_trabajadas && dia.horas_trabajadas > 0;

    if (tieneHoras) {
      // Verde muy tenue - similar al bg-primary pero con tinte verde
      pdf.setFillColor(20, 30, 26); // Verde oscuro muy tenue #141e1a
    } else {
      // Rojo muy tenue - similar al bg-primary pero con tinte rojo
      pdf.setFillColor(30, 20, 20); // Rojo oscuro muy tenue #1e1414
    }

    // Aplicar fondo a toda la fila
    for (let i = 0; i < columnWidths.length; i++) {
      const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);
      pdf.rect(x, currentY, columnWidths[i], maxRowHeight, 'F');
    }

    // Dibujar celdas de contenido
    pdf.setTextColor(200, 200, 200);
    for (let i = 0; i < row.length; i++) {
      const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);

      // Bordes sutiles
      pdf.setDrawColor(45, 55, 70);
      pdf.setLineWidth(0.2);
      pdf.rect(x, currentY, columnWidths[i], maxRowHeight);

      // Contenido
      const cellValue = String(row[i] || '-');
      const cellWidth = columnWidths[i] - 5;
      const lines = pdf.splitTextToSize(cellValue, cellWidth);

      const lineHeight = 6;
      const totalTextHeight = lines.length * lineHeight;
      const startTextY = currentY + (maxRowHeight - totalTextHeight) / 2 + 3.5;

      lines.forEach((line: string, lineIndex: number) => {
        pdf.text(line, x + columnWidths[i] / 2, startTextY + lineIndex * lineHeight, {
          align: 'center',
        });
      });
    }

    currentY += maxRowHeight;
  });

  // ========== FILA DE TOTALES (DENTRO DE LA TABLA) ==========
  const totalHeight = 10;

  // Verificar si cabe en la página actual
  if (currentY + totalHeight > pageBottom) {
    pdf.addPage();
    pdf.setFillColor(17, 21, 29); // #11151D
    pdf.rect(0, 0, pageWidth, pageHeight, 'F');
    currentY = margin;
  }

  // Primera celda combinada: "Total" (Día + Fecha + Entrada + Salida)
  const totalLabelWidth = columnWidths[0] + columnWidths[1] + columnWidths[2] + columnWidths[3];
  pdf.setFillColor(5, 46, 22); // Verde oscuro
  pdf.rect(startX, currentY, totalLabelWidth, totalHeight, 'F');
  pdf.setDrawColor(34, 197, 94); // Verde claro para borde
  pdf.setLineWidth(0.5);
  pdf.rect(startX, currentY, totalLabelWidth, totalHeight);

  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(8);
  pdf.setTextColor(34, 197, 94); // Verde claro
  pdf.text('Total', startX + totalLabelWidth / 2, currentY + totalHeight / 2 + 1.5, {
    align: 'center',
  });

  // Segunda celda: Valor del total (Horas Trabajadas)
  const totalValueWidth = columnWidths[4];
  const totalValueX = startX + totalLabelWidth;
  pdf.setFillColor(5, 46, 22);
  pdf.rect(totalValueX, currentY, totalValueWidth, totalHeight, 'F');
  pdf.setDrawColor(34, 197, 94);
  pdf.rect(totalValueX, currentY, totalValueWidth, totalHeight);

  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(34, 197, 94);
  pdf.text(totalFormato, totalValueX + totalValueWidth / 2, currentY + totalHeight / 2 + 1.5, {
    align: 'center',
  });

  currentY += totalHeight;

  return currentY;
}
