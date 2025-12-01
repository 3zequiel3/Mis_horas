from app import db
from datetime import datetime, timezone, timedelta

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class Proyecto(db.Model):
    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    
    # MIGRACIÓN MULTI-TENANT: organization_id reemplaza a usuario_id como owner principal
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False, index=True)
    # usuario_id se mantiene temporalmente para compatibilidad (será deprecado)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)
    
    activo = db.Column(db.Boolean, default=True)
    tipo_proyecto = db.Column(db.String(50), default='personal', nullable=False)  # 'personal' o 'empleados'
    horas_reales_activas = db.Column(db.Boolean, default=False)  # Activar/desactivar horas reales
    
    # Configuración de sistema de turnos
    modo_horarios = db.Column(db.String(20), default='corrido', nullable=False)  # 'corrido' o 'turnos'
    horario_inicio = db.Column(db.Time, nullable=True)  # Horario laboral inicio (para horas extras)
    horario_fin = db.Column(db.Time, nullable=True)  # Horario laboral fin (para horas extras)
    turno_manana_inicio = db.Column(db.Time, nullable=True)  # Inicio turno mañana
    turno_manana_fin = db.Column(db.Time, nullable=True)  # Fin turno mañana
    turno_tarde_inicio = db.Column(db.Time, nullable=True)  # Inicio turno tarde
    turno_tarde_fin = db.Column(db.Time, nullable=True)  # Fin turno tarde
    
    # FASE 4: Configuración Financiera y UX Unificada
    budget_type = db.Column(db.String(30), default='none', nullable=False)  # 'fixed_price', 'hourly_retainer', 'time_and_materials', 'none'
    budget_base_amount = db.Column(db.Numeric(12, 2), nullable=True)  # Monto base (dinero u horas según budget_type)
    currency = db.Column(db.String(3), default='USD', nullable=False)  # USD, EUR, ARS, etc.
    modules_config = db.Column(db.JSON, default=lambda: {
        'budget': False,
        'time_tracking': True,
        'audit': False,
        'approvals': False,
        'public_view': False
    }, nullable=False)  # Configuración de módulos activados
    brand_color = db.Column(db.String(7), nullable=True)  # Color hex para branding (ej: #3B82F6)
    client_name = db.Column(db.String(255), nullable=True)  # Nombre del cliente (opcional)
    
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), onupdate=lambda: datetime.now(LOCAL_TZ))

    # Relaciones
    organization = db.relationship("Organization", back_populates="proyectos")
    usuario = db.relationship("Usuario", back_populates="proyectos")  # Deprecated, mantener para compatibilidad
    dias = db.relationship("Dia", back_populates="proyecto", cascade="all, delete-orphan")
    tareas = db.relationship("Tarea", back_populates="proyecto", cascade="all, delete-orphan")
    empleados = db.relationship("Empleado", back_populates="proyecto", cascade="all, delete-orphan")

    def to_dict(self):
        """Convierte el proyecto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'anio': self.anio,
            'mes': self.mes,
            'organization_id': self.organization_id,
            'usuario_id': self.usuario_id,  # Deprecated pero se mantiene para compatibilidad
            'activo': self.activo,
            'tipo_proyecto': self.tipo_proyecto,
            'horas_reales_activas': self.horas_reales_activas,
            'modo_horarios': self.modo_horarios,
            'horario_inicio': self.horario_inicio.strftime('%H:%M') if self.horario_inicio else None,
            'horario_fin': self.horario_fin.strftime('%H:%M') if self.horario_fin else None,
            'turno_manana_inicio': self.turno_manana_inicio.strftime('%H:%M') if self.turno_manana_inicio else None,
            'turno_manana_fin': self.turno_manana_fin.strftime('%H:%M') if self.turno_manana_fin else None,
            'turno_tarde_inicio': self.turno_tarde_inicio.strftime('%H:%M') if self.turno_tarde_inicio else None,
            'turno_tarde_fin': self.turno_tarde_fin.strftime('%H:%M') if self.turno_tarde_fin else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'empleados': [e.to_dict() for e in self.empleados] if self.tipo_proyecto == 'empleados' else [],
            # Fase 4: Campos financieros y UX
            'budget_type': self.budget_type,
            'budget_base_amount': float(self.budget_base_amount) if self.budget_base_amount else None,
            'currency': self.currency,
            'modules_config': self.modules_config,
            'brand_color': self.brand_color,
            'client_name': self.client_name,
        }
