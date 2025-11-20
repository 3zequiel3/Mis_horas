-- ============================================================================
-- MIGRACIÓN: Agregar ON DELETE CASCADE a foreign keys
-- ============================================================================
-- Esta migración asegura que cuando se elimine un proyecto, todas las 
-- relaciones en tarea_dia se eliminen automáticamente
-- ============================================================================

USE timeflow_db;

-- Eliminar constraints existentes en tarea_dia
ALTER TABLE tarea_dia 
DROP FOREIGN KEY tarea_dia_ibfk_1,
DROP FOREIGN KEY tarea_dia_ibfk_2;

-- Recrear constraints con ON DELETE CASCADE
ALTER TABLE tarea_dia
ADD CONSTRAINT tarea_dia_ibfk_1 
    FOREIGN KEY (tarea_id) REFERENCES tareas(id) 
    ON DELETE CASCADE,
ADD CONSTRAINT tarea_dia_ibfk_2 
    FOREIGN KEY (dia_id) REFERENCES dias(id) 
    ON DELETE CASCADE;

-- Verificar cambios
SHOW CREATE TABLE tarea_dia\G

SELECT 'Migración completada: Foreign keys con CASCADE agregadas correctamente' AS Resultado;
