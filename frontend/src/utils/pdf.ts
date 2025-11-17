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
 * Dibuja una tabla en el PDF mejorada
 */
function drawTable(
  pdf: jsPDF,
  config: TableConfig,
  startX: number,
  startY: number
): number {
  const headers = config.headers;
  const rows = config.rows;
  const columnWidths = config.columnWidths || Array(headers.length).fill(180 / headers.length);
  const rowHeight = config.rowHeight || 8;
  const fontSize = 9;
  const headerFontSize = 10;

  let currentY = startY;
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;

  // Dibujar header
  pdf.setFontSize(headerFontSize);
  pdf.setFont('helvetica', 'bold');
  pdf.setFillColor(25, 73, 150); // Azul marino
  pdf.setTextColor(255, 255, 255); // Blanco

  let currentX = startX;
  headers.forEach((header, i) => {
    pdf.rect(currentX, currentY, columnWidths[i], rowHeight, 'F');
    pdf.setDrawColor(25, 73, 150);
    pdf.rect(currentX, currentY, columnWidths[i], rowHeight);
    
    pdf.text(header, currentX + 2, currentY + rowHeight / 2 + 1.5, {
      maxWidth: columnWidths[i] - 4,
      align: 'left',
    });
    currentX += columnWidths[i];
  });

  currentY += rowHeight;

  // Dibujar filas
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(fontSize);
  pdf.setTextColor(0, 0, 0);

  rows.forEach((row, rowIndex) => {
    // Verificar si necesita nueva página
    if (currentY + rowHeight > pageHeight - margin - 15) {
      pdf.addPage();
      currentY = margin;

      // Redibujar header en nueva página
      pdf.setFontSize(headerFontSize);
      pdf.setFont('helvetica', 'bold');
      pdf.setFillColor(25, 73, 150);
      pdf.setTextColor(255, 255, 255);

      let headerX = startX;
      headers.forEach((header, i) => {
        pdf.rect(headerX, currentY, columnWidths[i], rowHeight, 'F');
        pdf.setDrawColor(25, 73, 150);
        pdf.rect(headerX, currentY, columnWidths[i], rowHeight);
        
        pdf.text(header, headerX + 2, currentY + rowHeight / 2 + 1.5, {
          maxWidth: columnWidths[i] - 4,
          align: 'left',
        });
        headerX += columnWidths[i];
      });

      currentY += rowHeight;

      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(fontSize);
      pdf.setTextColor(0, 0, 0);
    }

    // Alternar colores de fila
    if (rowIndex % 2 === 0) {
      pdf.setFillColor(245, 245, 245);
      currentX = startX;
      columnWidths.forEach((width) => {
        pdf.rect(currentX, currentY, width, rowHeight, 'F');
        currentX += width;
      });
    }

    // Dibujar bordes y contenido
    currentX = startX;
    columnWidths.forEach((width, colIndex) => {
      pdf.setDrawColor(200, 200, 200);
      pdf.rect(currentX, currentY, width, rowHeight);

      const cellValue = String(row[colIndex] || '');
      pdf.setTextColor(0, 0, 0);
      
      // Alineación específica por columna
      let align: 'left' | 'center' = 'left';
      if (colIndex === 2) align = 'center'; // Horas centradas
      
      pdf.text(cellValue, currentX + 2, currentY + rowHeight / 2 + 1.5, {
        maxWidth: width - 4,
        align,
      });

      currentX += width;
    });

    currentY += rowHeight;
  });

  return currentY;
}

/**
 * Genera PDF de tareas con tabla mejorada
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
      orientation: 'landscape',
      unit: 'mm',
      format: 'a4',
    });

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 15;
    let currentY = margin;

    // Header profesional con fondo azul
    pdf.setFillColor(25, 73, 150); // Azul marino
    pdf.rect(0, 0, pageWidth, 35, 'F');

    // Título principal en blanco
    pdf.setFontSize(22);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(255, 255, 255);
    pdf.text(projectName, margin, 12);

    // Información del período
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Período: ${month} ${year}`, margin, 20);
    pdf.text(`Generado: ${new Date().toLocaleDateString('es-ES')}`, margin, 27);

    currentY = 40;

    // Preparar datos de la tabla
    const headers = ['Tarea', 'Detalle', 'Horas', '¿Qué Falta?', 'Días'];

    const rows = tareas.map((tarea) => {
      // Obtener días asociados a la tarea
      const diasAsociados = (tarea as any).dias
        ?.map((d: Dia) => new Date(d.fecha).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' }))
        .join(', ') || '-';

      return [
        tarea.titulo,
        tarea.detalle || '-',
        tarea.horas || '00:00',
        tarea.que_falta || '-',
        diasAsociados,
      ];
    });

    // Configurar ancho de columnas para landscape - mejor proporcionado
    const columnWidths = [28, 40, 18, 45, 45];

    // Configurar tabla
    const tableConfig: TableConfig = {
      headers,
      rows,
      columnWidths,
      rowHeight: 9,
    };

    // Dibujar tabla
    currentY = drawTable(pdf, tableConfig, margin, currentY);

    // Resumen al final
    if (tareas.length > 0) {
      currentY += 5;

      // Calcular totales
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

      // Panel de totales
      pdf.setFillColor(240, 245, 250); // Azul claro
      pdf.rect(margin, currentY, columnWidths.reduce((a, b) => a + b), 12, 'F');

      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(25, 73, 150);
      pdf.text(`Total de Tareas: ${tareas.length}`, margin + 2, currentY + 8);
      
      const totalX = margin + 60;
      pdf.text(`Total de Horas: ${totalFormato}`, totalX, currentY + 8);
    }

    // Footer numerado
    const pageCount = pdf.getNumberOfPages();
    pdf.setFontSize(8);
    pdf.setTextColor(150, 150, 150);
    pdf.setFont('helvetica', 'normal');

    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.text(
        `Página ${i} de ${pageCount}`,
        pageWidth - margin - 20,
        pageHeight - 8
      );
    }

    // Descargar PDF
    pdf.save(`${projectName}-${month}-${year}.pdf`);
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
