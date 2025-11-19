/**
 * Utilidades para generar PDFs - Modular y escalable
 * Soporta generación de tablas, títulos y contenido personalizado
 */

import jsPDF from 'jspdf';
import type { jsPDFOptions } from 'jspdf';
import html2canvas from 'html2canvas';
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
 * Genera un PDF básico desde HTML
 */
export async function generatePDFFromHTML(
  htmlElement: HTMLElement,
  options: PDFOptions
): Promise<void> {
  try {
    const canvas = await html2canvas(htmlElement, {
      scale: 2,
      backgroundColor: '#ffffff',
      logging: false,
    });

    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({
      orientation: (options.orientation || 'portrait') as 'portrait' | 'landscape',
      unit: 'mm',
      format: 'a4',
    });

    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const margin = options.margin || 10;

    const imgWidth = pdfWidth - margin * 2;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    pdf.addImage(imgData, 'PNG', margin, margin, imgWidth, imgHeight);
    pdf.save(options.fileName);
  } catch (error) {
    console.error('Error generando PDF:', error);
    throw error;
  }
}

/**
 * Dibuja una tabla en el PDF - ocupa todo el ancho con celdas centradas
 * Soporta contenido multilinea completo sin truncar
 * Colores inspirados en el tema oscuro de la aplicación
 */
function drawTable(
  pdf: jsPDF,
  config: TableConfig,
  startX: number,
  startY: number
): number {
  const headers = config.headers;
  const rows = config.rows;

  // Calcular ancho disponible (casi todo el ancho de la página)
  const pageWidth = pdf.internal.pageSize.getWidth();
  const totalAvailableWidth = pageWidth - 20; // 10mm margen a cada lado

  // Distribuir ancho equitativamente entre columnas
  const columnWidths = Array(headers.length).fill(totalAvailableWidth / headers.length);

  const fontSize = 9;
  const headerFontSize = 10;
  const minRowHeight = 8;

  let currentY = startY;
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;
  const pageBottom = pageHeight - margin - 12;

  // ========== DIBUJAR HEADERS ==========
  // Headers con color sólido (Purple de la app) - más profesional
  pdf.setFontSize(headerFontSize);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(255, 255, 255); // Texto blanco
  pdf.setLineWidth(0.4);

  const headerHeight = 11;
  for (let i = 0; i < headers.length; i++) {
    const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);

    // Relleno header - Purple sólido
    pdf.setFillColor(102, 126, 234); // Purple #667eea
    pdf.rect(x, currentY, columnWidths[i], headerHeight, 'F');

    // Borde sutil - sin colores que choquen
    pdf.setDrawColor(120, 140, 250); // Purple más claro para borde
    pdf.setLineWidth(0.4);
    pdf.rect(x, currentY, columnWidths[i], headerHeight);

    // Texto centrado - BLANCO PURO
    pdf.setTextColor(255, 255, 255);
    pdf.text(headers[i], x + columnWidths[i] / 2, currentY + headerHeight / 2 + 1.3, {
      maxWidth: columnWidths[i] - 2,
      align: 'center',
    });
  }

  currentY += headerHeight;

  // ========== DIBUJAR FILAS ==========
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(fontSize);
  pdf.setLineWidth(0.2);

  rows.forEach((row, rowIndex) => {
    // Calcular altura dinámicamente basada en el contenido
    let maxRowHeight = minRowHeight;

    for (let i = 0; i < row.length; i++) {
      const cellValue = String(row[i] || '-');
      const cellWidth = columnWidths[i] - 5; // Más margen interno

      // Usar splitTextToSize para calcular altura necesaria
      const lines = pdf.splitTextToSize(cellValue, cellWidth);
      // Aumentar espacio entre líneas y padding generosamente
      const cellHeight = lines.length * 6 + 6; // 6mm por línea + 6mm de padding

      if (cellHeight > maxRowHeight) {
        maxRowHeight = cellHeight;
      }
    }

    // Asegurar altura mínima
    if (maxRowHeight < minRowHeight) {
      maxRowHeight = minRowHeight;
    }

    // Verificar si necesita nueva página
    if (currentY + maxRowHeight > pageBottom) {
      pdf.addPage();

      // Fondo oscuro en nueva página
      pdf.setFillColor(15, 20, 25);
      pdf.rect(0, 0, pageWidth, pageHeight, 'F');

      currentY = margin;

      // Redibujar header en nueva página
      pdf.setFontSize(headerFontSize);
      pdf.setFont('helvetica', 'bold');
      pdf.setLineWidth(0.4);

      for (let i = 0; i < headers.length; i++) {
        const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);

        pdf.setFillColor(102, 126, 234); // Purple
        pdf.rect(x, currentY, columnWidths[i], headerHeight, 'F');
        pdf.setDrawColor(120, 140, 250); // Purple más claro
        pdf.rect(x, currentY, columnWidths[i], headerHeight);

        pdf.setTextColor(255, 255, 255);
        pdf.text(headers[i], x + columnWidths[i] / 2, currentY + headerHeight / 2 + 1.3, {
          maxWidth: columnWidths[i] - 2,
          align: 'center',
        });
      }

      currentY += headerHeight;
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(fontSize);
      pdf.setLineWidth(0.2);
    }

    // Color de fila alternada - oscuro sutil
    if (rowIndex % 2 === 0) {
      pdf.setFillColor(26, 26, 46); // bg-primary
      for (let i = 0; i < columnWidths.length; i++) {
        const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);
        pdf.rect(x, currentY, columnWidths[i], maxRowHeight, 'F');
      }
    } else {
      pdf.setFillColor(31, 41, 55); // gray-800
      for (let i = 0; i < columnWidths.length; i++) {
        const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);
        pdf.rect(x, currentY, columnWidths[i], maxRowHeight, 'F');
      }
    }

    // Dibujar celdas de contenido
    pdf.setTextColor(200, 200, 200); // Gris claro - mejor legibilidad
    for (let i = 0; i < row.length; i++) {
      const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);

      // Bordes muy sutiles
      pdf.setDrawColor(45, 55, 70); // Muy oscuro
      pdf.setLineWidth(0.2);
      pdf.rect(x, currentY, columnWidths[i], maxRowHeight);

      // Contenido multilinea
      const cellValue = String(row[i] || '-');
      const cellWidth = columnWidths[i] - 5; // Más margen interno
      const lines = pdf.splitTextToSize(cellValue, cellWidth);

      // Calcular posición vertical para centrar el texto
      const lineHeight = 6; // 6mm por línea para evitar superposición
      const totalTextHeight = lines.length * lineHeight;
      const startTextY = currentY + (maxRowHeight - totalTextHeight) / 2 + 3.5;

      // Dibujar cada línea centrada
      lines.forEach((line: string, lineIndex: number) => {
        pdf.text(line, x + columnWidths[i] / 2, startTextY + lineIndex * lineHeight, {
          align: 'center',
        });
      });
    }

    currentY += maxRowHeight;
  });

  return currentY;
}

/**
 * Genera PDF de tareas con tabla mejorada (estilo ReportLab)
 * Portrait compacto, tipografía profesional y legible
 */
export async function generateTasksPDF(
  projectName: string,
  month: string,
  year: number,
  tareas: Tarea[],
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
    const margin = 12;
    let currentY = 0;

    // ==================== FONDO OSCURO ====================
    // Llenar toda la página con fondo oscuro como en la app
    pdf.setFillColor(15, 20, 25); // #0f1419 - fondo oscuro de la app
    pdf.rect(0, 0, pageWidth, pageHeight, 'F');

    // ==================== HEADER - SIMPLIFICADO Y LIMPIO ====================
    // Header Purple sólido profesional
    pdf.setFillColor(102, 126, 234); // Purple #667eea
    pdf.rect(0, 0, pageWidth, 28, 'F');

    // Título principal - BLANCO PURO
    pdf.setFontSize(22);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(255, 255, 255);
    pdf.text(projectName, margin, 10);

    // Período
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(220, 220, 220);
    pdf.text(`${month} de ${year}`, margin, 18);

    // Fecha y hora de generación - Gris discreto
    pdf.setFontSize(8);
    pdf.setTextColor(180, 180, 180);
    const now = new Date();
    const dateStr = now.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
    const timeStr = now.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
    pdf.text(`Generado: ${dateStr} ${timeStr}`, margin, 25);

    currentY = 32;

    // ==================== TABLA ====================
    if (tareas.length === 0) {
      pdf.setFontSize(12);
      pdf.setTextColor(180, 180, 180);
      pdf.text('No hay tareas registradas', margin, currentY);
    } else {
      const headers = ['Tarea', 'Descripción', 'Horas', 'Días'];

      const rows = tareas.map((tarea) => {
        // Obtener días asociados a la tarea (SIN TRUNCAR)
        const diasAsociados = (tarea as any).dias
          ?.map((d: Dia) => new Date(d.fecha).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' }))
          .join(', ') || '-';

        return [
          tarea.titulo || '-', // SIN TRUNCAR
          tarea.detalle || '-', // SIN TRUNCAR - contenido completo
          tarea.horas || '00:00',
          diasAsociados, // SIN TRUNCAR
        ];
      });

      const tableConfig: TableConfig = {
        headers,
        rows,
      };

      currentY = drawTable(pdf, tableConfig, margin, currentY);

      // ==================== TOTALES ====================
      currentY += 6;

      let totalHorasNum = 0;
      tareas.forEach((tarea) => {
        const partes = (tarea.horas || '00:00').split(':');
        const horas = parseInt(partes[0]) || 0;
        const minutos = parseInt(partes[1]) || 0;
        totalHorasNum += horas + minutos / 60;
      });

      const horas = Math.floor(totalHorasNum);
      const minutos = Math.round((totalHorasNum - horas) * 60);
      const totalFormato = `${String(horas).padStart(2, '0')}:${String(minutos).padStart(2, '0')}`;

      // Panel de totales - ocupa casi todo el ancho
      const totalBoxWidth = pageWidth - 24; // Márgenes

      // Fondo oscuro con borde Green accent
      pdf.setFillColor(26, 26, 46); // bg-primary
      pdf.rect(margin, currentY, totalBoxWidth, 14, 'F');

      // Borde con Green accent - más visible
      pdf.setDrawColor(67, 233, 123); // Green #43e97b
      pdf.setLineWidth(1.8);
      pdf.rect(margin, currentY, totalBoxWidth, 14);

      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(67, 233, 123); // Green text - destaca

      const totalText = `TOTAL: ${tareas.length} tarea${tareas.length !== 1 ? 's' : ''} | ${totalFormato} hora${totalHorasNum !== 1 ? 's' : ''}`;
      pdf.text(totalText, margin + 4, currentY + 9);
    }

    // ==================== FOOTER ====================
    const pageCount = pdf.getNumberOfPages();
    pdf.setFontSize(8);
    pdf.setTextColor(107, 114, 128); // gray-500
    pdf.setFont('helvetica', 'normal');

    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);

      // Línea divisoria antes del footer
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
    const fileName = `MisHoras-${projectName}-${month.replace(/\s/g, '_')}-${year}.pdf`;
    pdf.save(fileName);
  } catch (error) {
    console.error('Error generando PDF de tareas:', error);
    throw error;
  }
}

/**
 * Genera un PDF de resumen general
 */
export async function generateSummaryPDF(
  projectName: string,
  month: string,
  year: number,
  totalHoras: string,
  totalTareas: number,
  diasTrabajados: number
): Promise<void> {
  try {
    const pdf = new jsPDF();
    const pageWidth = pdf.internal.pageSize.getWidth();
    const margin = 20;
    let currentY = margin;

    // Título
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Resumen de Proyecto', pageWidth / 2, currentY, { align: 'center' });

    currentY += 15;

    // Información del proyecto
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');

    const summaryData = [
      `Proyecto: ${projectName}`,
      `Período: ${month} ${year}`,
      `Total de Horas: ${totalHoras}`,
      `Total de Tareas: ${totalTareas}`,
      `Días Trabajados: ${diasTrabajados}`,
    ];

    summaryData.forEach((item) => {
      pdf.text(item, margin, currentY);
      currentY += 10;
    });

    pdf.save(`${projectName}-resumen-${month}-${year}.pdf`);
  } catch (error) {
    console.error('Error generando PDF de resumen:', error);
    throw error;
  }
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
 * Descarga un blob como archivo
 */
export function downloadBlob(blob: Blob, fileName: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
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
    const margin = 12;
    let currentY = 0;

    // ==================== FONDO OSCURO ====================
    pdf.setFillColor(15, 20, 25); // #0f1419
    pdf.rect(0, 0, pageWidth, pageHeight, 'F');

    // ==================== HEADER ====================
    pdf.setFillColor(102, 126, 234); // Purple #667eea
    pdf.rect(0, 0, pageWidth, 35, 'F');

    // Nombre del empleado - BLANCO PURO
    pdf.setFontSize(22);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(255, 255, 255);
    pdf.text(empleadoNombre, margin, 10);

    // Proyecto y período
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(220, 220, 220);
    pdf.text(`${proyectoNombre} - ${periodo}`, margin, 18);

    // Fecha de generación
    pdf.setFontSize(8);
    pdf.setTextColor(180, 180, 180);
    const now = new Date();
    const dateStr = now.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
    const timeStr = now.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
    pdf.text(`Generado: ${dateStr} ${timeStr}`, margin, 31);

    currentY = 39;

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
  const totalAvailableWidth = pageWidth - 20;

  // Distribuir ancho equitativamente
  const columnWidths = Array(headers.length).fill(totalAvailableWidth / headers.length);

  const fontSize = 9;
  const headerFontSize = 10;
  const minRowHeight = 8;

  let currentY = startY;
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;
  const pageBottom = pageHeight - margin - 12;

  // ========== DIBUJAR HEADERS ==========
  pdf.setFontSize(headerFontSize);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(255, 255, 255);
  pdf.setLineWidth(0.4);

  const headerHeight = 11;
  for (let i = 0; i < headers.length; i++) {
    const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);

    pdf.setFillColor(102, 126, 234); // Purple
    pdf.rect(x, currentY, columnWidths[i], headerHeight, 'F');

    pdf.setDrawColor(120, 140, 250);
    pdf.setLineWidth(0.4);
    pdf.rect(x, currentY, columnWidths[i], headerHeight);

    pdf.setTextColor(255, 255, 255);
    pdf.text(headers[i], x + columnWidths[i] / 2, currentY + headerHeight / 2 + 1.3, {
      maxWidth: columnWidths[i] - 2,
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
      pdf.setFillColor(15, 20, 25);
      pdf.rect(0, 0, pageWidth, pageHeight, 'F');
      currentY = margin;

      // Redibujar header
      pdf.setFontSize(headerFontSize);
      pdf.setFont('helvetica', 'bold');
      pdf.setLineWidth(0.4);

      for (let i = 0; i < headers.length; i++) {
        const x = startX + columnWidths.slice(0, i).reduce((a, b) => a + b, 0);
        pdf.setFillColor(102, 126, 234);
        pdf.rect(x, currentY, columnWidths[i], headerHeight, 'F');
        pdf.setDrawColor(120, 140, 250);
        pdf.rect(x, currentY, columnWidths[i], headerHeight);
        pdf.setTextColor(255, 255, 255);
        pdf.text(headers[i], x + columnWidths[i] / 2, currentY + headerHeight / 2 + 1.3, {
          maxWidth: columnWidths[i] - 2,
          align: 'center',
        });
      }

      currentY += headerHeight;
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(fontSize);
      pdf.setLineWidth(0.2);
    }

    // COLOR DE FONDO SEGÚN HORAS TRABAJADAS
    const tieneHoras = dia.horas_trabajadas && dia.horas_trabajadas > 0;

    if (tieneHoras) {
      // Verde tenue si tiene horas
      pdf.setFillColor(5, 46, 22); // Verde oscuro tenue #052e16
    } else {
      // Rojo tenue si no tiene horas
      pdf.setFillColor(69, 10, 10); // Rojo oscuro tenue #450a0a
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
    pdf.setFillColor(15, 20, 25);
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
