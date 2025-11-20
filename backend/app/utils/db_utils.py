"""
Utilidades para consultas comunes de base de datos.
Centraliza queries repetidas para evitar duplicación.
"""
from typing import Optional
from app.models import ConfiguracionAsistencia, Proyecto, Empleado


def obtener_configuracion_asistencia(proyecto_id: int) -> Optional[ConfiguracionAsistencia]:
    """
    Obtiene la configuración de asistencia de un proyecto.
    Patrón repetido en múltiples routes y services.
    
    Args:
        proyecto_id: ID del proyecto
    
    Returns:
        ConfiguracionAsistencia o None si no existe
    """
    return ConfiguracionAsistencia.query.filter_by(proyecto_id=proyecto_id).first()


def obtener_o_crear_configuracion_asistencia(
    proyecto_id: int,
    db_session
) -> ConfiguracionAsistencia:
    """
    Obtiene o crea una configuración de asistencia para un proyecto.
    Patrón repetido en routes de configuración.
    
    Args:
        proyecto_id: ID del proyecto
        db_session: Sesión de base de datos
    
    Returns:
        ConfiguracionAsistencia (existente o nueva)
    """
    config = ConfiguracionAsistencia.query.filter_by(proyecto_id=proyecto_id).first()
    
    if not config:
        config = ConfiguracionAsistencia(proyecto_id=proyecto_id)
        db_session.add(config)
    
    return config


def verificar_permiso_proyecto(proyecto, usuario_id: int) -> bool:
    """
    Verifica si un usuario tiene permisos sobre un proyecto.
    El usuario debe ser el propietario del proyecto.
    
    Args:
        proyecto: Objeto Proyecto
        usuario_id: ID del usuario
    
    Returns:
        True si tiene permisos, False en caso contrario
    """
    return proyecto.usuario_id == usuario_id


def verificar_empleado_en_proyecto(empleado_id: int, proyecto_id: int) -> bool:
    """
    Verifica si un empleado pertenece a un proyecto específico.
    
    Args:
        empleado_id: ID del empleado
        proyecto_id: ID del proyecto
    
    Returns:
        True si el empleado pertenece al proyecto, False en caso contrario
    """
    empleado = Empleado.query.get(empleado_id)
    if not empleado:
        return False
    
    return empleado.proyecto_id == proyecto_id
