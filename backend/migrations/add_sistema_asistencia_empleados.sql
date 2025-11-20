-- ================================================================
-- MIGRACIÓN: Sistema de Asistencia y Gestión de Empleados con Usuarios
-- Fecha: 2025-11-20
-- Descripción: Añade funcionalidad completa de invitaciones, notificaciones,
--              marcado de asistencia, gestión de deudas y justificaciones
-- ================================================================

-- ================================================================
-- 1. TABLA: Configuración de Asistencia por Proyecto
-- ================================================================
CREATE TABLE IF NOT EXISTS configuracion_asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT NOT NULL UNIQUE,
    
    -- Activación del sistema
    modo_asistencia_activo BOOLEAN DEFAULT FALSE,
    
    -- Políticas de gestión de horas extras vs deudas
    -- Opciones: 'compensar_deuda', 'bloquear_extras', 'separar_cuentas'
    politica_horas_extras ENUM('compensar_deuda', 'bloquear_extras', 'separar_cuentas') 
        DEFAULT 'compensar_deuda',
    
    -- Configuración de tolerancias
    tolerancia_retraso_minutos INT DEFAULT 15,  -- Tolerancia antes de alerta
    marcar_salida_automatica BOOLEAN DEFAULT TRUE,  -- Marca salida automática al fin de turno
    
    -- Configuración de justificaciones
    permitir_justificaciones BOOLEAN DEFAULT TRUE,
    requiere_aprobacion_justificaciones BOOLEAN DEFAULT TRUE,
    limite_horas_justificables INT DEFAULT NULL,  -- NULL = sin límite, ej: 40 horas/mes
    periodo_limite_justificaciones ENUM('diario', 'semanal', 'mensual', 'anual') DEFAULT 'mensual',
    
    -- Notificaciones y recordatorios
    enviar_recordatorio_marcado BOOLEAN DEFAULT TRUE,
    enviar_alerta_deuda BOOLEAN DEFAULT TRUE,
    hora_recordatorio_entrada TIME DEFAULT '09:00:00',
    hora_recordatorio_salida TIME DEFAULT '18:00:00',
    
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    INDEX idx_proyecto_asistencia (proyecto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================================
-- 2. TABLA: Relación Empleado-Usuario
-- ================================================================
-- Relaciona un empleado (registro del tablero) con un usuario del sistema
CREATE TABLE IF NOT EXISTS empleado_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empleado_id INT NOT NULL UNIQUE,
    usuario_id INT NOT NULL,
    
    -- Estado de la relación
    estado ENUM('pendiente', 'activo', 'inactivo') DEFAULT 'activo',
    rol_empleado ENUM('empleado', 'supervisor') DEFAULT 'empleado',
    
    -- Permisos específicos del empleado en este proyecto
    puede_ver_otros_empleados BOOLEAN DEFAULT FALSE,
    puede_exportar_propio_reporte BOOLEAN DEFAULT FALSE,
    
    fecha_asociacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_empleado (empleado_id),
    INDEX idx_usuario (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================================
-- 3. TABLA: Invitaciones a Proyectos
-- ================================================================
CREATE TABLE IF NOT EXISTS invitaciones_proyecto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT NOT NULL,
    empleado_id INT NOT NULL,
    
    -- Información del destinatario
    email_destinatario VARCHAR(255) NOT NULL,
    usuario_existente_id INT DEFAULT NULL,  -- NULL si el usuario no existe aún
    
    -- Estado y tokens
    estado ENUM('pendiente', 'aceptada', 'rechazada', 'expirada', 'cancelada') DEFAULT 'pendiente',
    token VARCHAR(255) NOT NULL UNIQUE,
    
    -- Mensaje personalizado del admin
    mensaje_invitacion TEXT,
    
    -- Control de tiempo
    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME NOT NULL,  -- Generalmente 7 días desde el envío
    fecha_respuesta DATETIME DEFAULT NULL,
    
    -- Tracking
    intentos_reenvio INT DEFAULT 0,
    ultima_fecha_reenvio DATETIME DEFAULT NULL,
    
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_existente_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    INDEX idx_token (token),
    INDEX idx_estado (estado),
    INDEX idx_email (email_destinatario),
    INDEX idx_proyecto (proyecto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================================
-- 4. TABLA: Notificaciones
-- ================================================================
CREATE TABLE IF NOT EXISTS notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    
    -- Tipo de notificación
    tipo ENUM(
        'invitacion_proyecto',
        'invitacion_aceptada',
        'invitacion_rechazada',
        'justificacion_enviada',
        'justificacion_aprobada',
        'justificacion_rechazada',
        'alerta_deuda',
        'recordatorio_marcado',
        'alerta_exceso_horario',
        'sistema'
    ) NOT NULL,
    
    -- Contenido
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    
    -- Estado
    leida BOOLEAN DEFAULT FALSE,
    archivada BOOLEAN DEFAULT FALSE,
    
    -- Metadatos (JSON para flexibilidad)
    metadatos JSON DEFAULT NULL,  -- Ej: {"proyecto_id": 5, "invitacion_id": 10}
    
    -- Acción asociada (opcional)
    url_accion VARCHAR(500) DEFAULT NULL,  -- URL a la que redirigir al hacer clic
    
    -- Fechas
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_lectura DATETIME DEFAULT NULL,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario_leida (usuario_id, leida),
    INDEX idx_tipo (tipo),
    INDEX idx_fecha (fecha_creacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================================
-- 5. TABLA: Marcados de Asistencia
-- ================================================================
CREATE TABLE IF NOT EXISTS marcados_asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empleado_id INT NOT NULL,
    proyecto_id INT NOT NULL,
    dia_id INT DEFAULT NULL,  -- Relación con la tabla días
    
    fecha DATE NOT NULL,
    
    -- Detección de turno
    turno ENUM('manana', 'tarde', 'nocturno', 'especial') DEFAULT NULL,
    
    -- Marcados de entrada/salida
    hora_entrada TIME DEFAULT NULL,
    hora_salida TIME DEFAULT NULL,
    
    -- Estado del marcado
    entrada_marcada_manualmente BOOLEAN DEFAULT FALSE,
    salida_marcada_manualmente BOOLEAN DEFAULT FALSE,
    salida_marcada_automaticamente BOOLEAN DEFAULT FALSE,
    
    -- Confirmación de trabajo continuo (cuando pasa el horario)
    confirmacion_continua BOOLEAN DEFAULT FALSE,
    confirmada_por_admin BOOLEAN DEFAULT FALSE,
    
    -- Cálculos
    horas_trabajadas DECIMAL(5,2) DEFAULT 0,
    horas_extras DECIMAL(5,2) DEFAULT 0,
    horas_normales DECIMAL(5,2) DEFAULT 0,
    
    -- Observaciones
    observaciones TEXT DEFAULT NULL,
    
    -- Geolocalización (opcional, para futuro)
    latitud_entrada DECIMAL(10, 8) DEFAULT NULL,
    longitud_entrada DECIMAL(11, 8) DEFAULT NULL,
    latitud_salida DECIMAL(10, 8) DEFAULT NULL,
    longitud_salida DECIMAL(11, 8) DEFAULT NULL,
    
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    FOREIGN KEY (dia_id) REFERENCES dias(id) ON DELETE SET NULL,
    INDEX idx_empleado_fecha (empleado_id, fecha),
    INDEX idx_proyecto (proyecto_id),
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================================
-- 6. TABLA: Deudas de Horas
-- ================================================================
CREATE TABLE IF NOT EXISTS deudas_horas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empleado_id INT NOT NULL,
    proyecto_id INT NOT NULL,
    
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE DEFAULT NULL,  -- NULL si es deuda actual
    
    -- Detalles de la deuda
    horas_debidas DECIMAL(5,2) NOT NULL DEFAULT 0,
    horas_justificadas DECIMAL(5,2) DEFAULT 0,
    horas_compensadas DECIMAL(5,2) DEFAULT 0,  -- Compensadas con horas extras
    
    -- Estado
    estado ENUM('activa', 'justificada', 'compensada', 'cerrada') DEFAULT 'activa',
    
    -- Motivo automático
    motivo ENUM('ausencia', 'salida_temprana', 'entrada_tardia', 'otro') NOT NULL,
    descripcion_automatica TEXT,  -- Generado por el sistema
    
    -- Cálculos
    horas_pendientes DECIMAL(5,2) AS (horas_debidas - horas_justificadas - horas_compensadas) STORED,
    
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    INDEX idx_empleado_estado (empleado_id, estado),
    INDEX idx_proyecto (proyecto_id),
    INDEX idx_fecha (fecha_inicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================================
-- 7. TABLA: Justificaciones
-- ================================================================
CREATE TABLE IF NOT EXISTS justificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deuda_id INT NOT NULL,
    empleado_id INT NOT NULL,
    proyecto_id INT NOT NULL,
    
    -- Detalles de la justificación
    motivo TEXT NOT NULL,
    horas_a_justificar DECIMAL(5,2) NOT NULL,
    
    -- Archivos adjuntos
    archivo_url VARCHAR(500) DEFAULT NULL,  -- Ruta al archivo subido
    archivo_nombre VARCHAR(255) DEFAULT NULL,
    archivo_tipo VARCHAR(100) DEFAULT NULL,  -- image/jpeg, application/pdf, etc.
    archivo_tamano INT DEFAULT NULL,  -- Tamaño en bytes
    
    -- Estado de aprobación
    estado ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT 'pendiente',
    
    -- Revisión del admin
    revisada_por_usuario_id INT DEFAULT NULL,
    fecha_revision DATETIME DEFAULT NULL,
    comentario_admin TEXT DEFAULT NULL,
    
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (deuda_id) REFERENCES deudas_horas(id) ON DELETE CASCADE,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    FOREIGN KEY (revisada_por_usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    INDEX idx_deuda (deuda_id),
    INDEX idx_estado (estado),
    INDEX idx_empleado (empleado_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================================
-- 8. MODIFICACIONES A TABLAS EXISTENTES
-- ================================================================

-- Agregar campos al modelo Empleado para tracking adicional (con validación)
SET @dbname = DATABASE();
SET @tablename = "empleados";

-- Agregar usuario_id si no existe
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'usuario_id') > 0,
  "SELECT 1",
  "ALTER TABLE empleados ADD COLUMN usuario_id INT DEFAULT NULL AFTER activo"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar estado_asistencia si no existe
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'estado_asistencia') > 0,
  "SELECT 1",
  "ALTER TABLE empleados ADD COLUMN estado_asistencia ENUM('activo', 'inactivo', 'suspendido') DEFAULT 'activo' AFTER usuario_id"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar horario_especial_inicio si no existe
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'horario_especial_inicio') > 0,
  "SELECT 1",
  "ALTER TABLE empleados ADD COLUMN horario_especial_inicio TIME DEFAULT NULL AFTER estado_asistencia"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar horario_especial_fin si no existe
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'horario_especial_fin') > 0,
  "SELECT 1",
  "ALTER TABLE empleados ADD COLUMN horario_especial_fin TIME DEFAULT NULL AFTER horario_especial_inicio"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar usa_horario_especial si no existe
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'usa_horario_especial') > 0,
  "SELECT 1",
  "ALTER TABLE empleados ADD COLUMN usa_horario_especial BOOLEAN DEFAULT FALSE AFTER horario_especial_fin"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar foreign key si no existe (verificar primero si la columna usuario_id tiene la FK)
SET @fk_exists = (SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
  WHERE TABLE_SCHEMA = @dbname 
    AND TABLE_NAME = @tablename 
    AND COLUMN_NAME = 'usuario_id' 
    AND REFERENCED_TABLE_NAME = 'usuarios'
);

SET @preparedStatement = IF(@fk_exists = 0,
  "ALTER TABLE empleados ADD FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL",
  "SELECT 1"
);
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ================================================================
-- 9. TRIGGERS Y PROCEDIMIENTOS ALMACENADOS
-- ================================================================

DELIMITER //

-- Trigger: Actualizar horas pendientes en deuda cuando se aprueba justificación
CREATE TRIGGER after_justificacion_aprobada
AFTER UPDATE ON justificaciones
FOR EACH ROW
BEGIN
    IF NEW.estado = 'aprobada' AND OLD.estado != 'aprobada' THEN
        UPDATE deudas_horas 
        SET horas_justificadas = horas_justificadas + NEW.horas_a_justificar
        WHERE id = NEW.deuda_id;
    END IF;
END//

-- Trigger: Crear notificación cuando se envía una invitación
CREATE TRIGGER after_invitacion_creada
AFTER INSERT ON invitaciones_proyecto
FOR EACH ROW
BEGIN
    IF NEW.usuario_existente_id IS NOT NULL THEN
        INSERT INTO notificaciones (
            usuario_id, 
            tipo, 
            titulo, 
            mensaje, 
            metadatos,
            url_accion
        ) VALUES (
            NEW.usuario_existente_id,
            'invitacion_proyecto',
            'Nueva invitación a proyecto',
            CONCAT('Has sido invitado a unirte al proyecto. Revisa los detalles.'),
            JSON_OBJECT('invitacion_id', NEW.id, 'proyecto_id', NEW.proyecto_id),
            CONCAT('/invitaciones/', NEW.id)
        );
    END IF;
END//

-- Trigger: Notificar al admin cuando se envía una justificación
CREATE TRIGGER after_justificacion_creada
AFTER INSERT ON justificaciones
FOR EACH ROW
BEGIN
    DECLARE admin_id INT;
    
    -- Obtener el usuario_id del admin del proyecto
    SELECT usuario_id INTO admin_id
    FROM proyectos
    WHERE id = NEW.proyecto_id;
    
    IF admin_id IS NOT NULL THEN
        INSERT INTO notificaciones (
            usuario_id, 
            tipo, 
            titulo, 
            mensaje, 
            metadatos,
            url_accion
        ) VALUES (
            admin_id,
            'justificacion_enviada',
            'Nueva justificación recibida',
            CONCAT('Un empleado ha enviado una justificación de horas. Requiere tu revisión.'),
            JSON_OBJECT('justificacion_id', NEW.id, 'proyecto_id', NEW.proyecto_id, 'empleado_id', NEW.empleado_id),
            CONCAT('/proyecto/', NEW.proyecto_id, '/justificaciones/', NEW.id)
        );
    END IF;
END//

DELIMITER ;

-- ================================================================
-- 10. ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ================================================================

-- Índice compuesto para búsquedas frecuentes de asistencia
CREATE INDEX idx_marcados_empleado_proyecto_fecha 
ON marcados_asistencia(empleado_id, proyecto_id, fecha DESC);

-- Índice para búsquedas de deudas activas
CREATE INDEX idx_deudas_activas 
ON deudas_horas(empleado_id, estado, fecha_inicio DESC);

-- Índice para notificaciones no leídas
CREATE INDEX idx_notificaciones_no_leidas 
ON notificaciones(usuario_id, leida, fecha_creacion DESC);

-- ================================================================
-- 11. DATOS INICIALES (OPCIONAL)
-- ================================================================

-- Insertar configuración de asistencia por defecto para proyectos existentes
INSERT INTO configuracion_asistencia (proyecto_id, modo_asistencia_activo)
SELECT id, FALSE FROM proyectos WHERE tipo_proyecto = 'empleados'
ON DUPLICATE KEY UPDATE proyecto_id = proyecto_id;

-- ================================================================
-- FIN DE MIGRACIÓN
-- ================================================================
