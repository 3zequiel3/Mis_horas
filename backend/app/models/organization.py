from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class Organization(db.Model):
    """
    Organización/Workspace - El contenedor de nivel superior para datos empresariales
    Cada organización es un "universo" independiente de datos
    """
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)  # URL-friendly
    
    # Información de la empresa
    descripcion = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.Text, nullable=True)  # URL del logo de la empresa
    
    # Configuración regional
    zona_horaria = db.Column(db.String(50), default='America/Argentina/Buenos_Aires')
    moneda = db.Column(db.String(3), default='ARS')  # ISO 4217 (USD, EUR, ARS, etc.)
    formato_fecha = db.Column(db.String(20), default='DD/MM/YYYY')
    
    # Dueño de la organización (quien la creó)
    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    
    # Tipo de organización
    tipo_organizacion = db.Column(
        db.Enum('personal', 'empresa', 'freelance', 'agencia', name='tipo_organizacion_enum'),
        default='personal',
        nullable=False
    )
    
    # Plan de suscripción (para futuro)
    plan_type = db.Column(
        db.Enum('free', 'starter', 'professional', 'enterprise', name='plan_type_enum'),
        default='free',
        nullable=False
    )
    
    # Estado
    activa = db.Column(db.Boolean, default=True, index=True)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_actualizacion = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(LOCAL_TZ), 
        onupdate=lambda: datetime.now(LOCAL_TZ)
    )
    
    # Límites por plan (para futuro)
    limite_proyectos = db.Column(db.Integer, nullable=True)  # NULL = ilimitado
    limite_miembros = db.Column(db.Integer, nullable=True)  # NULL = ilimitado
    limite_almacenamiento_mb = db.Column(db.Integer, nullable=True)  # NULL = ilimitado
    
    # Relaciones
    owner = db.relationship("Usuario", foreign_keys=[owner_id], backref="organizations_owned")
    members = db.relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    proyectos = db.relationship("Proyecto", back_populates="organization", cascade="all, delete-orphan")
    
    def to_dict(self, incluir_estadisticas=False):
        """Convierte la organización a diccionario"""
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'slug': self.slug,
            'descripcion': self.descripcion,
            'logo_url': self.logo_url,
            'zona_horaria': self.zona_horaria,
            'moneda': self.moneda,
            'formato_fecha': self.formato_fecha,
            'owner_id': self.owner_id,
            'tipo_organizacion': self.tipo_organizacion,
            'plan_type': self.plan_type,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
        
        if incluir_estadisticas:
            data['estadisticas'] = {
                'total_miembros': len(self.members),
                'total_proyectos': len(self.proyectos),
                'limite_proyectos': self.limite_proyectos,
                'limite_miembros': self.limite_miembros,
            }
        
        return data
    
    @staticmethod
    def generar_slug(nombre):
        """Genera un slug único a partir del nombre"""
        import re
        import secrets
        
        # Convertir a minúsculas y reemplazar espacios
        slug = nombre.lower()
        slug = re.sub(r'[áàäâ]', 'a', slug)
        slug = re.sub(r'[éèëê]', 'e', slug)
        slug = re.sub(r'[íìïî]', 'i', slug)
        slug = re.sub(r'[óòöô]', 'o', slug)
        slug = re.sub(r'[úùüû]', 'u', slug)
        slug = re.sub(r'[ñ]', 'n', slug)
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        
        # Verificar unicidad
        base_slug = slug
        counter = 1
        while Organization.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
