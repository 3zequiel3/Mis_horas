-- Migración: Agregar columnas hora_entrada y hora_salida a la tabla dias
-- Fecha: 2025-11-18
-- Descripción: Permite gestionar horarios de entrada/salida para empleados

ALTER TABLE dias 
ADD COLUMN hora_entrada TIME NULL AFTER horas_reales,
ADD COLUMN hora_salida TIME NULL AFTER hora_entrada;

-- Índices opcionales para mejorar rendimiento en consultas
CREATE INDEX idx_dias_horarios ON dias(hora_entrada, hora_salida);
