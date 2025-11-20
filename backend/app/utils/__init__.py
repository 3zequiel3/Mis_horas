# backend/app/utils/__init__.py

from .horario_utils import (
    obtener_horarios_turno,
    obtener_hora_cierre_turno,
    calcular_horas_esperadas,
    calcular_horas_extras,
    calcular_horas_debidas_dia,
    validar_configuracion_horarios
)

from .db_utils import (
    obtener_configuracion_asistencia,
    obtener_o_crear_configuracion_asistencia,
    verificar_permiso_proyecto,
    verificar_empleado_en_proyecto
)

__all__ = [
    # Horario utils
    'obtener_horarios_turno',
    'obtener_hora_cierre_turno',
    'calcular_horas_esperadas',
    'calcular_horas_extras',
    'calcular_horas_debidas_dia',
    'validar_configuracion_horarios',
    # DB utils
    'obtener_configuracion_asistencia',
    'obtener_o_crear_configuracion_asistencia',
    'verificar_permiso_proyecto',
    'verificar_empleado_en_proyecto'
]
