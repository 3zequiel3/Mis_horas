from app import db
from datetime import datetime, timezone, timedelta
import json

# Zona horaria local (Argentina: UTC-3)
LOCAL_TZ = timezone(timedelta(hours=-3))

class Notificacion(db.Model):
    __tablename__ = "notificaciones"

    id = db.Column(db.Integer, primary_key=True, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    
    # Tipo de notificación
    tipo = db.Column(
        db.Enum(
            'invitacion_proyecto',
            'invitacion_aceptada',
            'invitacion_rechazada',
            'justificacion_enviada',
            'justificacion_aprobada',
            'justificacion_rechazada',
            'alerta_deuda',
            'recordatorio_marcado',
            'alerta_exceso_horario',
            'salida_automatica',
            'confirmacion_horas_extras',
            'sistema',
            name='tipo_notificacion_enum'
        ),
        nullable=False,
        index=True
    )
    
    # Contenido
    titulo = db.Column(db.String(255), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    
    # Estado
    leida = db.Column(db.Boolean, default=False, index=True)
    archivada = db.Column(db.Boolean, default=False)
    
    # Metadatos (almacenado como string JSON)
    metadatos_json = db.Column('metadatos', db.Text, nullable=True)
    
    # Acción asociada
    url_accion = db.Column(db.String(500), nullable=True)
    
    # Fechas
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TZ), nullable=False, index=True)
    fecha_lectura = db.Column(db.DateTime, nullable=True)

    # Relaciones
    usuario = db.relationship("Usuario", backref="notificaciones")

    @property
    def metadatos(self):
        """Parsea el JSON de metadatos"""
        if self.metadatos_json:
            try:
                return json.loads(self.metadatos_json)
            except:
                return {}
        return {}

    @metadatos.setter
    def metadatos(self, value):
        """Guarda los metadatos como JSON"""
        if value:
            self.metadatos_json = json.dumps(value)
        else:
            self.metadatos_json = None

    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = datetime.now(LOCAL_TZ)
            db.session.commit()

    def to_dict(self):
        """Convierte la notificación a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'leida': self.leida,
            'archivada': self.archivada,
            'metadatos': self.metadatos,
            'url_accion': self.url_accion,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_lectura': self.fecha_lectura.isoformat() if self.fecha_lectura else None,
        }
