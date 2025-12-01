"""
Rutas API para gestión de organizaciones (Multi-Tenant)
Endpoints para CRUD de organizaciones y membresías
"""

from flask import Blueprint, request, jsonify
from app.services.organization_service import OrganizationService
from app.decorators import token_required, organization_required, requires_permission
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember

organization_bp = Blueprint('organizations', __name__)

# ============================================================
# GESTIÓN DE ORGANIZACIONES (Contexto de Usuario)
# ============================================================

@organization_bp.route('', methods=['GET'])
@token_required
def get_user_organizations(usuario_actual):
    """
    Obtiene todas las organizaciones del usuario autenticado
    Para el selector de contexto
    """
    try:
        organizations = OrganizationService.obtener_organizaciones_usuario(usuario_actual['id'])
        return jsonify([org.to_dict(incluir_estadisticas=True) for org in organizations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organization_bp.route('', methods=['POST'])
@token_required
def create_organization(usuario_actual):
    """
    Crea una nueva organización
    El usuario que la crea se convierte en owner automáticamente
    """
    data = request.get_json()
    
    if not data or 'nombre' not in data:
        return jsonify({'error': 'Campo requerido: nombre'}), 400
    
    try:
        org = OrganizationService.crear_organizacion(
            nombre=data['nombre'],
            owner_id=usuario_actual['id'],
            descripcion=data.get('descripcion'),
            tipo_organizacion=data.get('tipo_organizacion', 'empresa'),
            logo_url=data.get('logo_url')
        )
        
        return jsonify({
            'message': 'Organización creada exitosamente',
            'organization': org.to_dict(incluir_estadisticas=True)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# GESTIÓN DE ORGANIZACIÓN ESPECÍFICA (Con Contexto)
# ============================================================

@organization_bp.route('/<int:org_id>', methods=['GET'])
@token_required
def get_organization(usuario_actual, org_id):
    """Obtiene detalles de una organización específica"""
    # Verificar acceso
    if not OrganizationService.verificar_acceso(usuario_actual['id'], org_id):
        return jsonify({'error': 'No tienes acceso a esta organización'}), 403
    
    try:
        org = OrganizationService.obtener_organizacion(org_id)
        if not org:
            return jsonify({'error': 'Organización no encontrada'}), 404
        
        return jsonify(org.to_dict(incluir_estadisticas=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organization_bp.route('/<int:org_id>', methods=['PUT'])
@token_required
def update_organization(usuario_actual, org_id):
    """
    Actualiza configuración de una organización
    Solo owners y admins pueden modificar
    """
    # Verificar permisos
    membership = OrganizationMember.query.filter_by(
        user_id=usuario_actual['id'],
        organization_id=org_id,
        estado='activo'
    ).first()
    
    if not membership or membership.role not in ['owner', 'admin']:
        return jsonify({'error': 'No tienes permisos para modificar esta organización'}), 403
    
    data = request.get_json()
    
    try:
        org = OrganizationService.actualizar_organizacion(
            org_id=org_id,
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            logo_url=data.get('logo_url'),
            zona_horaria=data.get('zona_horaria'),
            moneda=data.get('moneda')
        )
        
        return jsonify({
            'message': 'Organización actualizada exitosamente',
            'organization': org.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organization_bp.route('/<int:org_id>', methods=['DELETE'])
@token_required
def delete_organization(usuario_actual, org_id):
    """
    Elimina una organización (soft delete)
    Solo el owner puede eliminar
    """
    try:
        OrganizationService.eliminar_organizacion(org_id, usuario_actual['id'])
        return jsonify({'message': 'Organización eliminada exitosamente'}), 200
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organization_bp.route('/<int:org_id>/stats', methods=['GET'])
@token_required
def get_organization_stats(usuario_actual, org_id):
    """Obtiene estadísticas de una organización"""
    # Verificar acceso
    if not OrganizationService.verificar_acceso(usuario_actual['id'], org_id):
        return jsonify({'error': 'No tienes acceso a esta organización'}), 403
    
    try:
        stats = OrganizationService.obtener_estadisticas(org_id)
        return jsonify(stats), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# GESTIÓN DE MIEMBROS
# ============================================================

@organization_bp.route('/<int:org_id>/members', methods=['GET'])
@token_required
def get_organization_members(usuario_actual, org_id):
    """Obtiene todos los miembros de una organización"""
    # Verificar acceso
    if not OrganizationService.verificar_acceso(usuario_actual['id'], org_id):
        return jsonify({'error': 'No tienes acceso a esta organización'}), 403
    
    try:
        members = OrganizationService.obtener_miembros(org_id)
        return jsonify([
            m.to_dict(incluir_usuario=True) for m in members
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organization_bp.route('/<int:org_id>/members/invite', methods=['POST'])
@token_required
def invite_member(usuario_actual, org_id):
    """
    Invita a un nuevo miembro a la organización por email
    Solo owners y admins pueden invitar
    """
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({'error': 'Campo requerido: email'}), 400
    
    role = data.get('role', 'member')
    if role not in ['admin', 'manager', 'member', 'viewer']:
        return jsonify({'error': 'Rol inválido'}), 400
    
    try:
        membership, es_nuevo = OrganizationService.invitar_miembro(
            org_id=org_id,
            email=data['email'],
            role=role,
            invitado_por_id=usuario_actual['id']
        )
        
        if es_nuevo:
            message = f"Invitación enviada a {data['email']}. Deberá crear una cuenta."
        else:
            message = f"Usuario agregado a la organización exitosamente."
        
        return jsonify({
            'message': message,
            'membership': membership.to_dict(incluir_usuario=True),
            'es_nuevo_usuario': es_nuevo
        }), 201
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organization_bp.route('/<int:org_id>/members/<int:user_id>', methods=['DELETE'])
@token_required
def remove_member(usuario_actual, org_id, user_id):
    """
    Remueve un miembro de la organización
    Solo owners y admins pueden remover
    """
    try:
        OrganizationService.remover_miembro(
            org_id=org_id,
            user_id=user_id,
            removido_por_id=usuario_actual['id']
        )
        
        return jsonify({'message': 'Miembro removido exitosamente'}), 200
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organization_bp.route('/<int:org_id>/members/<int:user_id>/role', methods=['PUT'])
@token_required
def change_member_role(usuario_actual, org_id, user_id):
    """
    Cambia el rol de un miembro
    Solo el owner puede cambiar roles
    """
    data = request.get_json()
    
    if not data or 'role' not in data:
        return jsonify({'error': 'Campo requerido: role'}), 400
    
    if data['role'] not in ['admin', 'manager', 'member', 'viewer']:
        return jsonify({'error': 'Rol inválido'}), 400
    
    try:
        membership = OrganizationService.cambiar_rol(
            org_id=org_id,
            user_id=user_id,
            nuevo_rol=data['role'],
            cambiado_por_id=usuario_actual['id']
        )
        
        return jsonify({
            'message': 'Rol actualizado exitosamente',
            'membership': membership.to_dict(incluir_usuario=True)
        }), 200
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# INVITACIONES (Usuario sin contexto organizacional)
# ============================================================

@organization_bp.route('/invitations/accept/<string:token>', methods=['POST'])
@token_required
def accept_invitation(usuario_actual, token):
    """
    Acepta una invitación a una organización
    Usado cuando un usuario registrado acepta unirse
    """
    try:
        membership = OrganizationService.aceptar_invitacion(
            token=token,
            user_id=usuario_actual['id']
        )
        
        return jsonify({
            'message': 'Te has unido a la organización exitosamente',
            'membership': membership.to_dict(incluir_organizacion=True)
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
