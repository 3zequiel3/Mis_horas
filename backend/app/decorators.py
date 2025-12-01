from flask import request, jsonify
from functools import wraps
from app.config import SECRET_KEY
import jwt

def get_token_from_request():
    """Extrae el token JWT del header Authorization"""
    import sys
    token = None
    
    sys.stderr.write(f"[DEBUG get_token] Headers: {dict(request.headers)}\n")
    sys.stderr.flush()
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        sys.stderr.write(f"[DEBUG get_token] Authorization header: {auth_header[:50]}...\n")
        sys.stderr.flush()
        try:
            token = auth_header.split(' ')[1]
            sys.stderr.write(f"[DEBUG get_token] Token extraído: {token[:20]}...\n")
            sys.stderr.flush()
        except IndexError:
            sys.stderr.write("[DEBUG get_token] Error al extraer token del header\n")
            sys.stderr.flush()
            return None
    else:
        sys.stderr.write("[DEBUG get_token] No se encontró header Authorization\n")
        sys.stderr.flush()
    
    return token

def validate_token():
    """Valida el token JWT y retorna el user_id o None"""
    token = get_token_from_request()
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = int(payload['identity'])
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_organization_context():
    """
    Extrae el ID de la organización del header X-Organization-ID
    Este header debe ser enviado por el frontend con cada request
    """
    org_id = request.headers.get('X-Organization-ID')
    if org_id:
        try:
            return int(org_id)
        except (ValueError, TypeError):
            return None
    return None

def token_required(f):
    """Decorador para validar token JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = validate_token()
        if not user_id:
            return jsonify({'error': 'Token requerido o inválido'}), 401
        
        # Crear objeto usuario_actual con la estructura esperada
        usuario_actual = {'id': user_id}
        
        return f(usuario_actual, *args, **kwargs)
    return decorated_function

def organization_required(f):
    """
    Decorador avanzado que valida token JWT + contexto organizacional
    Verifica que:
    1. El usuario esté autenticado
    2. Se envíe el header X-Organization-ID
    3. El usuario sea miembro activo de esa organización
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models.organization_member import OrganizationMember
        import sys
        
        # Validar token
        user_id = validate_token()
        sys.stderr.write(f"[DEBUG organization_required] user_id={user_id}\n")
        sys.stderr.flush()
        if not user_id:
            sys.stderr.write("[DEBUG organization_required] Token inválido o no presente\n")
            sys.stderr.flush()
            return jsonify({'error': 'Token requerido o inválido'}), 401
        
        # Obtener contexto organizacional
        org_id = get_organization_context()
        sys.stderr.write(f"[DEBUG organization_required] org_id={org_id}\n")
        sys.stderr.flush()
        if not org_id:
            sys.stderr.write("[DEBUG organization_required] Header X-Organization-ID no presente\n")
            sys.stderr.flush()
            return jsonify({
                'error': 'Contexto organizacional requerido',
                'message': 'Debe incluir el header X-Organization-ID'
            }), 400
        
        # Verificar membresía activa
        membership = OrganizationMember.query.filter_by(
            user_id=user_id,
            organization_id=org_id,
            estado='activo'
        ).first()
        sys.stderr.write(f"[DEBUG organization_required] membership={membership}\n")
        sys.stderr.flush()
        
        if not membership:
            sys.stderr.write(f"[DEBUG organization_required] No se encontró membresía activa para user_id={user_id}, org_id={org_id}\n")
            sys.stderr.flush()
            return jsonify({
                'error': 'Acceso denegado',
                'message': 'No eres miembro activo de esta organización'
            }), 403
        
        # Crear contexto enriquecido
        context = {
            'user_id': user_id,
            'organization_id': org_id,
            'role': membership.role,
            'membership': membership
        }
        
        return f(context, *args, **kwargs)
    return decorated_function

def requires_permission(permission):
    """
    Decorador que verifica permisos específicos basados en roles
    Debe usarse DESPUÉS de @organization_required
    
    Uso:
    @organization_required
    @requires_permission('view_finance')
    def get_finance_report(context):
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(context, *args, **kwargs):
            membership = context.get('membership')
            
            if not membership:
                return jsonify({'error': 'Contexto inválido'}), 500
            
            if not membership.tiene_permiso(permission):
                return jsonify({
                    'error': 'Permiso denegado',
                    'message': f'Tu rol ({membership.role}) no tiene permiso: {permission}'
                }), 403
            
            return f(context, *args, **kwargs)
        return decorated_function
    return decorator


# Helper functions para compatibilidad con código legacy
def get_current_user():
    """
    Función helper para obtener el user_id actual desde el token
    DEPRECATED: Usar @organization_required y context['user_id'] en su lugar
    """
    user_id = validate_token()
    if not user_id:
        from flask import abort
        abort(401, description="Token requerido o inválido")
    return user_id


def get_current_organization():
    """
    Función helper para obtener el organization_id actual desde el header
    DEPRECATED: Usar @organization_required y context['organization_id'] en su lugar
    """
    org_id = get_organization_context()
    if not org_id:
        from flask import abort
        abort(400, description="Header X-Organization-ID requerido")
    return org_id