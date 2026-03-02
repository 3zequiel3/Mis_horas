"""
Rutas para gestión de colaboradores en proyectos colaborativos
"""

from flask import Blueprint, request
from app.decorators import organization_required
from app.services.colaboradores_service import ColaboradoresService
from app.utils.response import success_response, error_response

colaboradores_bp = Blueprint('colaboradores', __name__, url_prefix='/api/proyectos')


@colaboradores_bp.route('/<int:proyecto_id>/convertir-colaborativo', methods=['POST'])
@organization_required
def convertir_colaborativo(context, proyecto_id):
    """
    Convierte un proyecto personal a colaborativo
    """
    try:
        from app.models.proyecto import Proyecto
        
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return error_response("Proyecto no encontrado", 404)
        
        # Verificar permisos (solo el dueño puede convertir)
        if proyecto.usuario_id != context['user_id']:
            return error_response("Solo el dueño del proyecto puede convertirlo a colaborativo", 403)
        
        # Verificar que el proyecto pertenece a la organización
        if proyecto.organization_id != context['organization_id']:
            return error_response("El proyecto no pertenece a esta organización", 403)
        
        proyecto_actualizado, error = ColaboradoresService.convertir_a_colaborativo(
            proyecto_id,
            context['user_id']
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'proyecto': proyecto_actualizado.to_dict()},
            message='Proyecto convertido a colaborativo exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al convertir proyecto: {str(e)}', 500)


@colaboradores_bp.route('/<int:proyecto_id>/colaboradores', methods=['GET'])
@organization_required
def listar_colaboradores(context, proyecto_id):
    """
    Lista todos los colaboradores de un proyecto
    Query params: incluir_estadisticas (boolean)
    """
    try:
        from app.models.proyecto import Proyecto
        
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return error_response("Proyecto no encontrado", 404)
        
        # Verificar acceso
        tiene_acceso, es_owner, config = ColaboradoresService.verificar_acceso_colaborador(
            proyecto_id,
            context['user_id']
        )
        
        if not tiene_acceso:
            return error_response("No tienes acceso a este proyecto", 403)
        
        incluir_estadisticas = request.args.get('incluir_estadisticas', 'false').lower() == 'true'
        
        colaboradores = ColaboradoresService.listar_colaboradores(
            proyecto_id,
            incluir_estadisticas=incluir_estadisticas
        )
        
        return success_response(
            data={'colaboradores': colaboradores},
            message=f'Se encontraron {len(colaboradores)} colaboradores'
        )
        
    except Exception as e:
        return error_response(f'Error al listar colaboradores: {str(e)}', 500)


@colaboradores_bp.route('/<int:proyecto_id>/colaboradores', methods=['POST'])
@organization_required
def invitar_colaborador(context, proyecto_id):
    """
    Invita a un usuario a ser colaborador del proyecto
    Body: { "email": "usuario@ejemplo.com", "horas_reales_activas": true/false }
    """
    try:
        from app.models.proyecto import Proyecto
        
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return error_response("Proyecto no encontrado", 404)
        
        # Solo el owner puede invitar
        tiene_acceso, es_owner, config = ColaboradoresService.verificar_acceso_colaborador(
            proyecto_id,
            context['user_id']
        )
        
        if not es_owner:
            return error_response("Solo el dueño del proyecto puede invitar colaboradores", 403)
        
        data = request.get_json()
        email = data.get('email', '').strip()
        horas_reales_activas = data.get('horas_reales_activas', False)
        
        if not email:
            return error_response("Email requerido", 400)
        
        colaborador, error = ColaboradoresService.invitar_colaborador(
            proyecto_id,
            email,
            horas_reales_activas
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'colaborador': colaborador.to_dict(incluir_usuario=True)},
            message='Colaborador agregado exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al invitar colaborador: {str(e)}', 500)


@colaboradores_bp.route('/<int:proyecto_id>/colaboradores/<int:usuario_id>', methods=['DELETE'])
@organization_required
def eliminar_colaborador(context, proyecto_id, usuario_id):
    """
    Elimina un colaborador del proyecto
    """
    try:
        from app.models.proyecto import Proyecto
        
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return error_response("Proyecto no encontrado", 404)
        
        # Verificar que es owner
        tiene_acceso, es_owner, config = ColaboradoresService.verificar_acceso_colaborador(
            proyecto_id,
            context['user_id']
        )
        
        if not es_owner:
            return error_response("Solo el dueño puede eliminar colaboradores", 403)
        
        exito, error = ColaboradoresService.eliminar_colaborador(
            proyecto_id,
            usuario_id,
            context['user_id']
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            message='Colaborador eliminado exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al eliminar colaborador: {str(e)}', 500)


@colaboradores_bp.route('/<int:proyecto_id>/colaboradores/<int:usuario_id>/config', methods=['PUT'])
@organization_required
def actualizar_configuracion_colaborador(context, proyecto_id, usuario_id):
    """
    Actualiza la configuración de un colaborador
    Body: { "horas_reales_activas": true/false }
    """
    try:
        from app.models.proyecto import Proyecto
        
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return error_response("Proyecto no encontrado", 404)
        
        # Solo el owner puede cambiar configuración
        tiene_acceso, es_owner, config = ColaboradoresService.verificar_acceso_colaborador(
            proyecto_id,
            context['user_id']
        )
        
        if not es_owner:
            return error_response("Solo el dueño puede modificar la configuración", 403)
        
        data = request.get_json()
        horas_reales_activas = data.get('horas_reales_activas')
        
        if horas_reales_activas is None:
            return error_response("horas_reales_activas requerido", 400)
        
        colaborador, error = ColaboradoresService.actualizar_configuracion_colaborador(
            proyecto_id,
            usuario_id,
            horas_reales_activas
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'colaborador': colaborador.to_dict(incluir_usuario=True)},
            message='Configuración actualizada exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al actualizar configuración: {str(e)}', 500)


@colaboradores_bp.route('/<int:proyecto_id>/colaboradores/estadisticas', methods=['GET'])
@organization_required
def obtener_estadisticas(context, proyecto_id):
    """
    Obtiene estadísticas generales del proyecto colaborativo
    """
    try:
        from app.models.proyecto import Proyecto
        
        proyecto = Proyecto.query.get(proyecto_id)
        
        if not proyecto:
            return error_response("Proyecto no encontrado", 404)
        
        # Verificar acceso
        tiene_acceso, es_owner, config = ColaboradoresService.verificar_acceso_colaborador(
            proyecto_id,
            context['user_id']
        )
        
        if not tiene_acceso:
            return error_response("No tienes acceso a este proyecto", 403)
        
        estadisticas = ColaboradoresService.obtener_estadisticas_proyecto(proyecto_id)
        
        if not estadisticas:
            return error_response("No se pudieron obtener las estadísticas", 400)
        
        return success_response(
            data={'estadisticas': estadisticas},
            message='Estadísticas obtenidas exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al obtener estadísticas: {str(e)}', 500)
