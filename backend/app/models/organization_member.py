from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class OrganizationMember(db.Model):
    """
    Membresía de usuario en una organización
    Define qué usuarios pertenecen a qué organizaciones y con qué rol
    """
    __tablename__ = "organization_members"

    id = db.Column(db.Integer, primary_key=True, index=True)
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Rol del usuario en esta organización
    role = db.Column(
        db.Enum(
            'owner',        # Dueño (control total, ve todo, gestiona suscripción)
            'admin',        # Administrador (gestiona proyectos, empleados, ve costos)
            'manager',      # Manager (gestiona tareas, aprueba horas, NO ve salarios)
            'member',       # Miembro (solo registra sus horas)
            'viewer',       # Observador (solo lectura)
            name='organization_role_enum'
        ),
        nullable=False,
        default='member'
    )
    
    # Estado de la membresía
    estado = db.Column(
        db.Enum('activo', 'suspendido', 'invitado', name='member_status_enum'),
        default='activo',
        nullable=False,
        index=True
    )
    
    # Invitación (si aplica)
    invitado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    token_invitacion = db.Column(db.String(255), unique=True, nullable=True, index=True)
    fecha_invitacion = db.Column(db.DateTime, nullable=True)
    fecha_aceptacion = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    fecha_ingreso = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_salida = db.Column(db.DateTime, nullable=True)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    
    # Preferencias del miembro
    notificaciones_email = db.Column(db.Boolean, default=True)
    notificaciones_push = db.Column(db.Boolean, default=True)
    
    # Relaciones
    usuario = db.relationship("Usuario", foreign_keys=[user_id], backref="memberships")
    organization = db.relationship("Organization", back_populates="members")
    invitado_por = db.relationship("Usuario", foreign_keys=[invitado_por_id])
    
    # Índice compuesto para evitar membresías duplicadas
    __table_args__ = (
        db.UniqueConstraint('user_id', 'organization_id', name='unique_user_organization'),
        db.Index('idx_org_user_status', 'organization_id', 'user_id', 'estado'),
    )
    
    def to_dict(self, incluir_usuario=False, incluir_organizacion=False):
        """Convierte la membresía a diccionario"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'role': self.role,
            'estado': self.estado,
            'fecha_ingreso': self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            'fecha_salida': self.fecha_salida.isoformat() if self.fecha_salida else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            'notificaciones_email': self.notificaciones_email,
            'notificaciones_push': self.notificaciones_push,
        }
        
        if incluir_usuario and self.usuario:
            data['usuario'] = {
                'id': self.usuario.id,
                'username': self.usuario.username,
                'email': self.usuario.email,
                'nombre_completo': self.usuario.nombre_completo,
                'foto_perfil': self.usuario.foto_perfil,
            }
        
        if incluir_organizacion and self.organization:
            data['organization'] = self.organization.to_dict()
        
        if self.invitado_por_id and self.invitado_por:
            data['invitado_por'] = {
                'id': self.invitado_por.id,
                'nombre_completo': self.invitado_por.nombre_completo,
            }
        
        return data
    
    def tiene_permiso(self, permiso):
        """
        Verifica si el rol del miembro tiene un permiso específico
        Sistema de permisos basado en roles (RBAC)
        """
        permisos_por_rol = {
            'owner': [
                'view_all', 'edit_all', 'delete_all',
                'manage_organization', 'manage_billing', 'manage_members',
                'manage_projects', 'view_finance', 'edit_finance',
                'approve_hours', 'view_team_hours',
            ],
            'admin': [
                'view_all', 'edit_all',
                'manage_members', 'manage_projects',
                'view_finance', 'edit_finance',
                'approve_hours', 'view_team_hours',
            ],
            'manager': [
                'view_all', 'edit_projects',
                'approve_hours', 'view_team_hours',
            ],
            'member': [
                'view_own', 'edit_own',
            ],
            'viewer': [
                'view_all',
            ],
        }
        
        return permiso in permisos_por_rol.get(self.role, [])
    
    @staticmethod
    def generar_token_invitacion():
        """Genera un token único para invitaciones"""
        import secrets
        return secrets.token_urlsafe(32)
