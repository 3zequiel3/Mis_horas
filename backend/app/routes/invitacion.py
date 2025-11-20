"""
Rutas para gestión de invitaciones a proyectos
"""

from flask import Blueprint, request, jsonify
from app.decorators import token_required
from app.services.invitacion_service import InvitacionService
from app.utils.response import success_response, error_response

invitacion_bp = Blueprint('invitaciones', __name__, url_prefix='/api/invitaciones')


@invitacion_bp.route('/buscar-usuarios', methods=['GET'])
@token_required
def buscar_usuarios(usuario_actual):
    """
    Busca usuarios en el sistema por username, email o nombre
    Query params: q (query de búsqueda), limit (default: 10)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query or len(query) < 2:
            return error_response('Debes proporcionar al menos 2 caracteres para buscar', 400)
        
        usuarios = InvitacionService.buscar_usuarios(query, limit)
        
        return success_response(
            data={'usuarios': usuarios},
            message=f'Se encontraron {len(usuarios)} usuarios'
        )
        
    except Exception as e:
        return error_response(f'Error al buscar usuarios: {str(e)}', 500)


@invitacion_bp.route('/verificar-email', methods=['POST'])
@token_required
def verificar_email(usuario_actual):
    """
    Verifica si un email existe en el sistema y si hay invitaciones previas
    Body: { "email": "usuario@ejemplo.com", "empleado_id": 5 }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        empleado_id = data.get('empleado_id')
        
        if not email:
            return error_response('Email requerido', 400)
        
        existe, usuario = InvitacionService.verificar_email_existe(email)
        
        response_data = {
            'existe': existe,
            'usuario': usuario.to_dict() if usuario else None,
            'invitacion_previa': None,
            'puede_reenviar': False
        }
        
        # Si se proporciona empleado_id, verificar invitaciones previas
        if empleado_id:
            invitacion, puede_reenviar = InvitacionService.verificar_invitacion_existente(
                empleado_id, 
                email
            )
            
            if invitacion:
                response_data['invitacion_previa'] = invitacion.to_dict()
                response_data['puede_reenviar'] = puede_reenviar
        
        return success_response(data=response_data)
        
    except Exception as e:
        return error_response(f'Error al verificar email: {str(e)}', 500)


@invitacion_bp.route('/enviar', methods=['POST'])
@token_required
def enviar_invitacion(usuario_actual):
    """
    Envía una invitación para asociar un empleado con un usuario
    Body: {
        "proyecto_id": 1,
        "empleado_id": 5,
        "email_destinatario": "empleado@ejemplo.com",
        "mensaje_invitacion": "Bienvenido al equipo" (opcional)
    }
    """
    try:
        data = request.get_json()
        print(f"📧 Datos recibidos para invitación: {data}")
        
        proyecto_id = data.get('proyecto_id')
        empleado_id = data.get('empleado_id')
        email_destinatario = data.get('email_destinatario', '').strip()
        mensaje_invitacion = data.get('mensaje_invitacion')
        
        # Validaciones
        if not all([proyecto_id, empleado_id, email_destinatario]):
            print(f"❌ Faltan datos: proyecto_id={proyecto_id}, empleado_id={empleado_id}, email={email_destinatario}")
            return error_response('proyecto_id, empleado_id y email_destinatario son requeridos', 400)
        
        # Crear invitación
        invitacion, error = InvitacionService.crear_invitacion(
            proyecto_id=proyecto_id,
            empleado_id=empleado_id,
            email_destinatario=email_destinatario,
            admin_usuario_id=usuario_actual['id'],
            mensaje_invitacion=mensaje_invitacion
        )
        
        if error:
            print(f"❌ Error del servicio: {error}")
            return error_response(error, 400)
        
        print(f"✅ Invitación creada exitosamente: {invitacion.id}")
        return success_response(
            data={'invitacion': invitacion.to_dict()},
            message='Invitación enviada exitosamente'
        )
        
    except Exception as e:
        print(f"💥 Excepción en enviar_invitacion: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Error al enviar invitación: {str(e)}', 500)


@invitacion_bp.route('/mis-invitaciones', methods=['GET'])
@token_required
def obtener_mis_invitaciones(usuario_actual):
    """
    Obtiene las invitaciones del usuario actual
    Query params: incluir_expiradas (default: false)
    """
    try:
        incluir_expiradas = request.args.get('incluir_expiradas', 'false').lower() == 'true'
        
        invitaciones = InvitacionService.obtener_invitaciones_usuario(
            usuario_actual['id'],
            incluir_expiradas
        )
        
        return success_response(
            data={'invitaciones': invitaciones},
            message=f'Se encontraron {len(invitaciones)} invitaciones'
        )
        
    except Exception as e:
        return error_response(f'Error al obtener invitaciones: {str(e)}', 500)


@invitacion_bp.route('/<token>/aceptar', methods=['POST'])
@token_required
def aceptar_invitacion(usuario_actual, token):
    """
    Acepta una invitación
    """
    try:
        invitacion, error = InvitacionService.aceptar_invitacion(token, usuario_actual['id'])
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'invitacion': invitacion.to_dict()},
            message='Invitación aceptada exitosamente. Ahora formas parte del proyecto.'
        )
        
    except Exception as e:
        return error_response(f'Error al aceptar invitación: {str(e)}', 500)


@invitacion_bp.route('/<token>/rechazar', methods=['POST'])
@token_required
def rechazar_invitacion(usuario_actual, token):
    """
    Rechaza una invitación
    Body: { "motivo": "Razón del rechazo" } (opcional)
    """
    try:
        data = request.get_json() or {}
        motivo = data.get('motivo')
        
        invitacion, error = InvitacionService.rechazar_invitacion(
            token, 
            usuario_actual['id'],
            motivo
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'invitacion': invitacion.to_dict()},
            message='Invitación rechazada'
        )
        
    except Exception as e:
        return error_response(f'Error al rechazar invitación: {str(e)}', 500)


@invitacion_bp.route('/<int:invitacion_id>/reenviar', methods=['POST'])
@token_required
def reenviar_invitacion(usuario_actual, invitacion_id):
    """
    Reenvía una invitación existente
    """
    try:
        invitacion, error = InvitacionService.reenviar_invitacion(
            invitacion_id,
            usuario_actual['id']
        )
        
        if error:
            return error_response(error, 400)
        
        return success_response(
            data={'invitacion': invitacion.to_dict()},
            message='Invitación reenviada exitosamente'
        )
        
    except Exception as e:
        return error_response(f'Error al reenviar invitación: {str(e)}', 500)


@invitacion_bp.route('/validar/<string:token>', methods=['GET'])
def validar_token_invitacion(token):
    """
    Valida un token de invitación y devuelve sus datos (sin autenticación)
    """
    try:
        from app.models.invitacion_proyecto import InvitacionProyecto
        from app.models.proyecto import Proyecto
        from app.models.empleado import Empleado
        
        invitacion = InvitacionProyecto.query.filter_by(token=token).first()
        
        if not invitacion:
            return error_response('Invitación no encontrada', 404)
        
        if not invitacion.esta_vigente():
            return error_response('La invitación ha expirado', 400)
        
        if invitacion.estado not in ['pendiente', 'expirada']:
            return error_response(f'Esta invitación ya fue {invitacion.estado}', 400)
        
        # Obtener datos adicionales
        proyecto = Proyecto.query.get(invitacion.proyecto_id)
        empleado = Empleado.query.get(invitacion.empleado_id)
        
        invitacion_dict = invitacion.to_dict()
        invitacion_dict['proyecto_nombre'] = proyecto.nombre if proyecto else 'Desconocido'
        invitacion_dict['empleado_nombre'] = empleado.nombre if empleado else 'Desconocido'
        
        return success_response(
            data={'invitacion': invitacion_dict},
            message='Token válido'
        )
        
    except Exception as e:
        return error_response(f'Error al validar token: {str(e)}', 500)


@invitacion_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@token_required
def obtener_invitaciones_proyecto(usuario_actual, proyecto_id):
    """
    Obtiene todas las invitaciones de un proyecto (solo admin)
    """
    try:
        from app.models.proyecto import Proyecto
        from app.models.invitacion_proyecto import InvitacionProyecto
        
        print(f"📋 Obteniendo invitaciones del proyecto {proyecto_id} para usuario {usuario_actual['id']}")
        
        # Verificar permisos
        proyecto = Proyecto.query.get(proyecto_id)
        if not proyecto:
            print(f"❌ Proyecto {proyecto_id} no encontrado")
            return error_response('Proyecto no encontrado', 404)
            
        if proyecto.usuario_id != usuario_actual['id']:
            print(f"❌ Usuario {usuario_actual['id']} no tiene permisos sobre proyecto {proyecto_id}")
            return error_response('No tienes permisos para ver las invitaciones de este proyecto', 403)
        
        invitaciones = InvitacionProyecto.query.filter_by(proyecto_id=proyecto_id).order_by(
            InvitacionProyecto.fecha_envio.desc()
        ).all()
        
        print(f"✅ Se encontraron {len(invitaciones)} invitaciones")
        
        return success_response(
            data={'invitaciones': [inv.to_dict() for inv in invitaciones]},
            message=f'Se encontraron {len(invitaciones)} invitaciones'
        )
        
    except Exception as e:
        print(f"💥 Excepción en obtener_invitaciones_proyecto: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'Error al obtener invitaciones del proyecto: {str(e)}', 500)
