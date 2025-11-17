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
      const cellWidth = columnWidths[i] - 3;
      
      // Usar splitTextToSize para calcular altura necesaria
      const lines = pdf.splitTextToSize(cellValue, cellWidth);
      const cellHeight = lines.length * 4.5 + 2;
      
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
      const cellWidth = columnWidths[i] - 3;
      const lines = pdf.splitTextToSize(cellValue, cellWidth);
      
      // Calcular posición vertical para centrar el texto
      const totalTextHeight = lines.length * 4.5;
      const startTextY = currentY + (maxRowHeight - totalTextHeight) / 2 + 2;
      
      // Dibujar cada línea centrada
      lines.forEach((line: string, lineIndex: number) => {
        pdf.text(line, x + columnWidths[i] / 2, startTextY + lineIndex * 4.5, {
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
