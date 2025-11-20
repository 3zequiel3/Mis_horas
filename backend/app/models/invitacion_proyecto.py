from app import db
from datetime import datetime, timezone, timedelta
import secrets

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class InvitacionProyecto(db.Model):
    __tablename__ = "invitaciones_proyecto"

    id = db.Column(db.Integer, primary_key=True, index=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=False)
    
    # Información del destinatario
    email_destinatario = db.Column(db.String(255), nullable=False, index=True)
    usuario_existente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    
    # Estado y tokens
    estado = db.Column(
        db.Enum('pendiente', 'aceptada', 'rechazada', 'expirada', 'cancelada', name='estado_invitacion_enum'),
        default='pendiente',
        index=True
    )
    token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # Mensaje personalizado del admin
    mensaje_invitacion = db.Column(db.Text, nullable=True)
    
    # Control de tiempo
    fecha_envio = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False)
    fecha_expiracion = db.Column(db.DateTime, nullable=False)
    fecha_respuesta = db.Column(db.DateTime, nullable=True)
    
    # Tracking
    intentos_reenvio = db.Column(db.Integer, default=0)
    ultima_fecha_reenvio = db.Column(db.DateTime, nullable=True)

    # Relaciones
    proyecto = db.relationship("Proyecto", backref="invitaciones")
    empleado = db.relationship("Empleado", backref="invitaciones")
    usuario_existente = db.relationship("Usuario", backref="invitaciones_recibidas")

    @staticmethod
    def generar_token():
        """Genera un token único para la invitación"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def crear_fecha_expiracion(dias=7):
        """Crea una fecha de expiración (por defecto 7 días)"""
        return datetime.now(LOCAL_TZ) + timedelta(days=dias)

    def esta_vigente(self):
        """Verifica si la invitación está vigente"""
        ahora = datetime.now(LOCAL_TZ)
        # Si fecha_expiracion no tiene timezone, agregarla
        fecha_exp = self.fecha_expiracion
        if fecha_exp.tzinfo is None:
            fecha_exp = fecha_exp.replace(tzinfo=LOCAL_TZ)
        
        return (
            self.estado == 'pendiente' and
            fecha_exp > ahora
        )

    def to_dict(self):
        """Convierte la invitación a diccionario"""
        result = {
            'id': self.id,
            'proyecto_id': self.proyecto_id,
            'empleado_id': self.empleado_id,
            'email_destinatario': self.email_destinatario,
            'usuario_existente_id': self.usuario_existente_id,
            'estado': self.estado,
            'token': self.token,
            'mensaje_invitacion': self.mensaje_invitacion,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
            'fecha_expiracion': self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            'fecha_respuesta': self.fecha_respuesta.isoformat() if self.fecha_respuesta else None,
            'intentos_reenvio': self.intentos_reenvio,
            'ultima_fecha_reenvio': self.ultima_fecha_reenvio.isoformat() if self.ultima_fecha_reenvio else None,
            'esta_vigente': self.esta_vigente(),
        }
        
        # Agregar info del empleado si existe
        if self.empleado:
            result['empleado_nombre'] = self.empleado.nombre
            
        # Agregar info del proyecto si existe
        if self.proyecto:
            result['proyecto_nombre'] = self.proyecto.nombre
            
        return result
