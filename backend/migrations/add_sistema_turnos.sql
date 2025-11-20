-- ============================================
-- Migración: Sistema de Turnos
-- Fecha: 2025-11-19
-- Descripción: Agrega funcionalidad de turnos configurables por proyecto
-- ============================================

USE timeflow_db;

-- 1. Agregar columnas a tabla proyectos para configuración de turnos
ALTER TABLE proyectos 
  ADD COLUMN modo_horarios ENUM('corrido', 'turnos') DEFAULT 'corrido' COMMENT 'Modo de registro: corrido (entrada/salida única) o turnos (múltiples bloques)',
  ADD COLUMN horario_inicio TIME NULL COMMENT 'Hora de inicio del horario laboral (para cálculo de horas extras)',
  ADD COLUMN horario_fin TIME NULL COMMENT 'Hora de fin del horario laboral (para cálculo de horas extras)',
  ADD COLUMN turno_manana_inicio TIME NULL COMMENT 'Hora de inicio del turno mañana',
  ADD COLUMN turno_manana_fin TIME NULL COMMENT 'Hora de fin del turno mañana',
  ADD COLUMN turno_tarde_inicio TIME NULL COMMENT 'Hora de inicio del turno tarde',
  ADD COLUMN turno_tarde_fin TIME NULL COMMENT 'Hora de fin del turno tarde';

-- 2. Agregar columnas a tabla dias para registrar entrada/salida por turno
ALTER TABLE dias 
  ADD COLUMN turno_manana_entrada TIME NULL COMMENT 'Hora de entrada del turno mañana',
  ADD COLUMN turno_manana_salida TIME NULL COMMENT 'Hora de salida del turno mañana',
  ADD COLUMN turno_tarde_entrada TIME NULL COMMENT 'Hora de entrada del turno tarde',
  ADD COLUMN turno_tarde_salida TIME NULL COMMENT 'Hora de salida del turno tarde',
  ADD COLUMN horas_extras DECIMAL(5,2) DEFAULT 0 COMMENT 'Horas extras trabajadas en el día';

-- 3. Crear índices para optimizar consultas
CREATE INDEX idx_proyectos_modo_horarios ON proyectos(modo_horarios);
CREATE INDEX idx_dias_horas_extras ON dias(horas_extras);

-- ============================================
-- Notas de migración:
-- ============================================
-- 1. Los proyectos existentes quedarán en modo 'corrido' por defecto (retrocompatibilidad)
-- 2. Las columnas de turnos son NULL para permitir que no se usen si el modo es 'corrido'
-- 3. La columna horas_extras se calculará automáticamente en el backend
-- 4. Los datos existentes en 'entrada' y 'salida' se mantienen intactos
-- ============================================
