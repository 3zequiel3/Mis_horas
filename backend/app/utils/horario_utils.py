"""
Utilidades para cálculo y manejo de horarios laborales.
Centraliza la lógica repetida de horarios en diferentes servicios.
"""
from datetime import datetime, date, timedelta
from typing import Tuple, Optional
from time import time as get_time


def obtener_horarios_turno(proyecto, turno: Optional[str] = None) -> Tuple[Optional[object], Optional[object]]:
    """
    Obtiene el horario de inicio y fin según el modo de horarios del proyecto y turno.
    
    Args:
        proyecto: Objeto Proyecto con configuración de horarios
        turno: 'manana', 'tarde' o None para modo corrido
    
    Returns:
        Tupla (hora_inicio, hora_fin) como objetos time
    """
    if proyecto.modo_horarios == 'turnos':
        if turno == 'manana':
            return proyecto.turno_manana_inicio, proyecto.turno_manana_fin
        elif turno == 'tarde':
            return proyecto.turno_tarde_inicio, proyecto.turno_tarde_fin
        else:
            # Turno especial o no definido, usar horario general
            return proyecto.horario_inicio, proyecto.horario_fin
    else:
        # Modo corrido
        return proyecto.horario_inicio, proyecto.horario_fin


def obtener_hora_cierre_turno(proyecto, turno: Optional[str] = None) -> Optional[object]:
    """
    Obtiene la hora de cierre según el turno y modo de horarios.
    
    Args:
        proyecto: Objeto Proyecto con configuración de horarios
        turno: 'manana', 'tarde' o None para modo corrido
    
    Returns:
        Objeto time con la hora de cierre o None
    """
    if proyecto.modo_horarios == 'corrido':
        return proyecto.horario_fin
    elif proyecto.modo_horarios == 'turnos':
        if turno == 'manana':
            return proyecto.turno_manana_fin
        elif turno == 'tarde':
            return proyecto.turno_tarde_fin
        else:
            # Turno especial o no definido, usar horario general
            return proyecto.horario_fin
    
    return None


def calcular_horas_esperadas(hora_inicio, hora_fin) -> float:
    """
    Calcula las horas esperadas entre dos horarios.
    Maneja correctamente horarios que cruzan medianoche.
    
    Args:
        hora_inicio: Objeto time con hora de inicio
        hora_fin: Objeto time con hora de fin
    
    Returns:
        Horas esperadas como float
    """
    if not hora_inicio or not hora_fin:
        return 0.0
    
    hora_inicio_dt = datetime.combine(date.today(), hora_inicio)
    hora_fin_dt = datetime.combine(date.today(), hora_fin)
    
    # Si la hora de fin es menor o igual a la de inicio, cruza medianoche
    if hora_fin_dt <= hora_inicio_dt:
        hora_fin_dt += timedelta(days=1)
    
    return (hora_fin_dt - hora_inicio_dt).total_seconds() / 3600


def calcular_horas_extras(
    horas_trabajadas: float,
    proyecto,
    turno: Optional[str] = None
) -> Tuple[float, float]:
    """
    Calcula las horas extras y normales según el turno y configuración del proyecto.
    
    Args:
        horas_trabajadas: Total de horas trabajadas
        proyecto: Objeto Proyecto con configuración de horarios
        turno: 'manana', 'tarde' o None para modo corrido
    
    Returns:
        Tupla (horas_normales, horas_extras) redondeadas a 2 decimales
    """
    horas_trabajadas = float(horas_trabajadas)
    
    # Obtener horario laboral esperado
    hora_inicio, hora_fin = obtener_horarios_turno(proyecto, turno)
    
    if not hora_inicio or not hora_fin:
        return horas_trabajadas, 0.0
    
    # Calcular horas esperadas
    horas_esperadas = calcular_horas_esperadas(hora_inicio, hora_fin)
    
    # Calcular horas extras
    if horas_trabajadas > horas_esperadas:
        horas_extras = horas_trabajadas - horas_esperadas
        horas_normales = horas_esperadas
    else:
        horas_extras = 0.0
        horas_normales = horas_trabajadas
    
    return round(horas_normales, 2), round(horas_extras, 2)


def calcular_horas_debidas_dia(proyecto, empleado=None, turno: Optional[str] = None) -> float:
    """
    Calcula las horas que el empleado debe trabajar en un día según configuración.
    
    Args:
        proyecto: Objeto Proyecto con configuración de horarios
        empleado: Objeto Empleado (opcional, para horarios personalizados)
        turno: 'manana', 'tarde' o None para modo corrido
    
    Returns:
        Horas debidas como float
    """
    # TODO: Implementar horarios personalizados por empleado
    # if empleado and empleado.horario_personalizado:
    #     return calcular_horas_esperadas(
    #         empleado.horario_inicio,
    #         empleado.horario_fin
    #     )
    
    if proyecto.modo_horarios == 'turnos':
        # En turnos, calcular horas de ambos turnos si aplica
        horas_dia = 0.0
        
        if proyecto.turno_manana_inicio and proyecto.turno_manana_fin:
            horas_manana = calcular_horas_esperadas(
                proyecto.turno_manana_inicio,
                proyecto.turno_manana_fin
            )
            horas_dia += horas_manana
        
        if proyecto.turno_tarde_inicio and proyecto.turno_tarde_fin:
            horas_tarde = calcular_horas_esperadas(
                proyecto.turno_tarde_inicio,
                proyecto.turno_tarde_fin
            )
            horas_dia += horas_tarde
        
        return horas_dia
    
    elif proyecto.modo_horarios == 'corrido':
        # En modo corrido, usar horario general
        if proyecto.horario_inicio and proyecto.horario_fin:
            return calcular_horas_esperadas(
                proyecto.horario_inicio,
                proyecto.horario_fin
            )
    
    return 0.0


def validar_configuracion_horarios(proyecto) -> Tuple[bool, Optional[str]]:
    """
    Valida que el proyecto tenga configuración de horarios válida.
    
    Args:
        proyecto: Objeto Proyecto a validar
    
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not proyecto.modo_horarios or proyecto.modo_horarios == 'corrido':
        if not proyecto.horario_inicio or not proyecto.horario_fin:
            return False, 'Debes configurar los horarios laborales del proyecto'
    
    elif proyecto.modo_horarios == 'turnos':
        # Verificar que al menos un turno esté configurado
        tiene_turno_manana = proyecto.turno_manana_inicio and proyecto.turno_manana_fin
        tiene_turno_tarde = proyecto.turno_tarde_inicio and proyecto.turno_tarde_fin
        
        if not tiene_turno_manana and not tiene_turno_tarde:
            return False, 'Debes configurar al menos un turno (mañana o tarde)'
    
    return True, None
