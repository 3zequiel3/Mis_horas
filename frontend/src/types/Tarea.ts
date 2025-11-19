/**
 * Tipos relacionados con Tarea
 */

import type { Dia } from './Dia';

export interface Tarea {
  id: number;
  titulo: string;
  detalle?: string;
  horas: string;
  que_falta?: string;
  proyecto_id: number;
  dias?: Dia[];
  creado_en?: string;
  actualizado_en?: string;
}

export interface CreateTareaRequest {
  titulo: string;
  detalle?: string;
  horas?: string;
  que_falta?: string;
  proyecto_id: number;
  dias_ids?: number[];
}

export interface UpdateTareaRequest {
  titulo?: string;
  detalle?: string;
  horas?: string;
  que_falta?: string;
}

export interface TareaListItem {
  tarea: Tarea;
  diasCount: number;
}
