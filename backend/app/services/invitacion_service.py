"""
Servicio para gestión de invitaciones a proyectos
"""

from app import db
from app.models import InvitacionProyecto, Notificacion, Empleado, Usuario, Proyecto, EmpleadoUsuario
from app.services.email_service import EmailService
from datetime import datetime, timezone, timedelta
from sqlalchemy import and_, or_

LOCAL_TZ = timezone(timedelta(hours=-3))


class InvitacionService:
    """Servicio para manejar invitaciones a proyectos"""
    
    @staticmethod
    def buscar_usuarios(query: str, limit: int = 10):
        """
        Busca usuarios en el sistema por username o email
        
        Args:
            query: Término de búsqueda
            limit: Cantidad máxima de resultados
        
        Returns:
            Lista de usuarios encontrados
        """
        usuarios = Usuario.query.filter(
            or_(
                Usuario.username.ilike(f'%{query}%'),
                Usuario.email.ilike(f'%{query}%'),
                Usuario.nombre_completo.ilike(f'%{query}%')
            )
        ).filter(Usuario.activo == True).limit(limit).all()
        
        return [u.to_dict() for u in usuarios]
    
    @staticmethod
    def verificar_email_existe(email: str):
        """Verifica si un email ya existe en el sistema"""
        usuario = Usuario.query.filter_by(email=email).first()
        return usuario is not None, usuario
    
    @staticmethod
    def verificar_invitacion_existente(empleado_id: int, email_destinatario: str):
        """Verifica si ya existe una invitación para este empleado y email"""
        invitacion = InvitacionProyecto.query.filter(
            and_(
                InvitacionProyecto.empleado_id == empleado_id,
                InvitacionProyecto.email_destinatario == email_destinatario
            )
        ).order_by(InvitacionProyecto.fecha_envio.desc()).first()
        
        if not invitacion:
            return None, None
        
        # Determinar si se puede reenviar
        puede_reenviar = (
            invitacion.estado == 'pendiente' or 
            invitacion.estado == 'expirada'
        )
        
        return invitacion, puede_reenviar
    
    @staticmethod
    def crear_invitacion(
        proyecto_id: int,
        empleado_id: int,
        email_destinatario: str,
        admin_usuario_id: int,
        mensaje_invitacion: str = None
    ):
        """
        Crea una invitación para asociar un empleado con un usuario
        
        Args:
            proyecto_id: ID del proyecto
            empleado_id: ID del empleado a asociar
            email_destinatario: Email del usuario a invitar
            admin_usuario_id: ID del usuario admin que envía la invitación
            mensaje_invitacion: Mensaje personalizado opcional
        
        Returns:
            Invitación creada o None si hay error
        """
        try:
            # Verificar que el proyecto y empleado existen
            proyecto = Proyecto.query.get(proyecto_id)
            empleado = Empleado.query.get(empleado_id)
            admin = Usuario.query.get(admin_usuario_id)
            
            if not proyecto or not empleado or not admin:
                return None, "Proyecto, empleado o admin no encontrado"
            
            # Verificar que el admin es dueño del proyecto
            if proyecto.usuario_id != admin_usuario_id:
                return None, "No tienes permisos para enviar invitaciones en este proyecto"
            
            # Verificar si el empleado ya está asociado a un usuario
            if empleado.usuario_id is not None:
                return None, "El empleado ya está asociado a un usuario"
            
            # Verificar si ya existe una invitación para este empleado
            invitacion_existente = InvitacionProyecto.query.filter(
                InvitacionProyecto.empleado_id == empleado_id
            ).order_by(InvitacionProyecto.fecha_envio.desc()).first()
            
            # Si existe una invitación vigente y pendiente, devolver info para reenvío
            if invitacion_existente:
                if invitacion_existente.estado == 'pendiente' and invitacion_existente.esta_vigente():
                    return None, f"Ya existe una invitación pendiente vigente. Usa el botón 'Reenviar' si necesitas enviarla nuevamente (ID: {invitacion_existente.id})"
                elif invitacion_existente.estado == 'aceptada':
                    return None, "Este empleado ya aceptó una invitación anterior"
                # Si está expirada, rechazada o cancelada, se puede crear una nueva (continuar)
            
            # Verificar si el email existe en el sistema
            email_existe, usuario_existente = InvitacionService.verificar_email_existe(email_destinatario)
            
            # Crear la invitación
            invitacion = InvitacionProyecto(
                proyecto_id=proyecto_id,
                empleado_id=empleado_id,
                email_destinatario=email_destinatario,
                usuario_existente_id=usuario_existente.id if usuario_existente else None,
                token=InvitacionProyecto.generar_token(),
                mensaje_invitacion=mensaje_invitacion,
                fecha_expiracion=InvitacionProyecto.crear_fecha_expiracion()
            )
            
            db.session.add(invitacion)
            db.session.commit()
            
            # Enviar email de invitación (si falla, no romper el proceso)
            try:
                EmailService.enviar_invitacion_proyecto(
                    email_destinatario=email_destinatario,
                    nombre_proyecto=proyecto.nombre,
                    nombre_admin=admin.nombre_completo or admin.username,
                    token=invitacion.token,
                    mensaje_personalizado=mensaje_invitacion,
                    es_nuevo_usuario=not email_existe
                )
            except Exception as email_error:
                print(f"⚠️ No se pudo enviar el email de invitación: {str(email_error)}")
                # Continuar aunque falle el email - la invitación se creó correctamente
            
            return invitacion, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear invitación: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def aceptar_invitacion(token: str, usuario_id: int):
        """
        Acepta una invitación y asocia el empleado al usuario
        
        Args:
            token: Token de la invitación
            usuario_id: ID del usuario que acepta
        
        Returns:
            Resultado de la operación
        """
        try:
            # Buscar la invitación
            invitacion = InvitacionProyecto.query.filter_by(token=token).first()
            
            if not invitacion:
                return None, "Invitación no encontrada"
            
            if not invitacion.esta_vigente():
                invitacion.estado = 'expirada'
                db.session.commit()
                return None, "La invitación ha expirado"
            
            # Verificar que el usuario que acepta es el destinatario correcto
            usuario = Usuario.query.get(usuario_id)
            if not usuario or usuario.email != invitacion.email_destinatario:
                return None, "No tienes permisos para aceptar esta invitación"
            
            # Verificar que el empleado existe y no esté ya asociado
            empleado = Empleado.query.get(invitacion.empleado_id)
            if not empleado:
                return None, "El empleado no existe o fue eliminado"
                
            if empleado.usuario_id is not None:
                return None, "El empleado ya está asociado a otro usuario"
            
            # Asociar empleado con usuario
            empleado.usuario_id = usuario_id
            empleado.estado_asistencia = 'activo'
            
            # Crear relación en empleado_usuario
            empleado_usuario = EmpleadoUsuario(
                empleado_id=empleado.id,
                usuario_id=usuario_id,
                estado='activo',
                rol_empleado='empleado'
            )
            
            db.session.add(empleado_usuario)
            
            # Actualizar estado de la invitación
            invitacion.estado = 'aceptada'
            invitacion.fecha_respuesta = datetime.now(LOCAL_TZ)
            
            db.session.commit()
            
            # Notificar al admin
            proyecto = Proyecto.query.get(invitacion.proyecto_id)
            notificacion = Notificacion(
                usuario_id=proyecto.usuario_id,
                tipo='invitacion_aceptada',
                titulo='Invitación aceptada',
                mensaje=f'{usuario.nombre_completo or usuario.username} ha aceptado tu invitación al proyecto {proyecto.nombre}',
                metadatos={'invitacion_id': invitacion.id, 'proyecto_id': proyecto.id, 'empleado_id': empleado.id},
                url_accion=f'/proyecto/{proyecto.id}'
            )
            db.session.add(notificacion)
            db.session.commit()
            
            return invitacion, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al aceptar invitación: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def aceptar_invitacion_con_token(token: str, usuario_id: int):
        """
        Acepta una invitación durante el registro (usuario recién creado)
        Similar a aceptar_invitacion pero más permisivo con validaciones
        
        Args:
            token: Token de la invitación
            usuario_id: ID del usuario recién registrado
        
        Returns:
            (invitacion, error_message)
        """
        try:
            # Buscar la invitación
            invitacion = InvitacionProyecto.query.filter_by(token=token).first()
            
            if not invitacion:
                return None, "Invitación no encontrada"
            
            if not invitacion.esta_vigente():
                invitacion.estado = 'expirada'
                db.session.commit()
                return None, "La invitación ha expirado"
            
            # Obtener usuario y empleado
            usuario = Usuario.query.get(usuario_id)
            empleado = Empleado.query.get(invitacion.empleado_id)
            
            if not usuario or not empleado:
                return None, "Usuario o empleado no encontrado"
            
            # Verificar que el email coincida
            if usuario.email != invitacion.email_destinatario:
                return None, "El email no coincide con la invitación"
            
            # Verificar que el empleado no esté ya asociado
            if empleado.usuario_id is not None:
                return None, "El empleado ya está asociado a otro usuario"
            
            # Asociar empleado con usuario
            empleado.usuario_id = usuario_id
            empleado.estado_asistencia = 'activo'
            
            # Crear relación en empleado_usuario
            empleado_usuario = EmpleadoUsuario(
                empleado_id=empleado.id,
                usuario_id=usuario_id,
                estado='activo',
                rol_empleado='empleado'
            )
            
            db.session.add(empleado_usuario)
            
            # Actualizar estado de la invitación
            invitacion.estado = 'aceptada'
            invitacion.fecha_respuesta = datetime.now(LOCAL_TZ)
            
            db.session.commit()
            
            # Notificar al admin
            proyecto = Proyecto.query.get(invitacion.proyecto_id)
            notificacion = Notificacion(
                usuario_id=proyecto.usuario_id,
                tipo='invitacion_aceptada',
                titulo='Invitación aceptada',
                mensaje=f'{usuario.nombre_completo or usuario.username} ha aceptado tu invitación al proyecto {proyecto.nombre}',
                metadatos={'invitacion_id': invitacion.id, 'proyecto_id': proyecto.id, 'empleado_id': empleado.id},
                url_accion=f'/proyecto/{proyecto.id}'
            )
            db.session.add(notificacion)
            db.session.commit()
            
            return invitacion, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al aceptar invitación con token: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def rechazar_invitacion(token: str, usuario_id: int, motivo: str = None):
        """
        Rechaza una invitación
        
        Args:
            token: Token de la invitación
            usuario_id: ID del usuario que rechaza
            motivo: Motivo del rechazo (opcional)
        
        Returns:
            Resultado de la operación
        """
        try:
            invitacion = InvitacionProyecto.query.filter_by(token=token).first()
            
            if not invitacion:
                return None, "Invitación no encontrada"
            
            if not invitacion.esta_vigente():
                return None, "La invitación ha expirado"
            
            # Verificar que el usuario que rechaza es el destinatario
            usuario = Usuario.query.get(usuario_id)
            if not usuario or usuario.email != invitacion.email_destinatario:
                return None, "No tienes permisos para rechazar esta invitación"
            
            # Actualizar estado
            invitacion.estado = 'rechazada'
            invitacion.fecha_respuesta = datetime.now(LOCAL_TZ)
            
            db.session.commit()
            
            # Notificar al admin
            proyecto = Proyecto.query.get(invitacion.proyecto_id)
            notificacion = Notificacion(
                usuario_id=proyecto.usuario_id,
                tipo='invitacion_rechazada',
                titulo='Invitación rechazada',
                mensaje=f'{usuario.nombre_completo or usuario.username} ha rechazado tu invitación al proyecto {proyecto.nombre}',
                metadatos={'invitacion_id': invitacion.id, 'proyecto_id': proyecto.id, 'motivo': motivo},
                url_accion=f'/proyecto/{proyecto.id}'
            )
            db.session.add(notificacion)
            db.session.commit()
            
            return invitacion, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al rechazar invitación: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def obtener_invitaciones_usuario(usuario_id: int, incluir_expiradas: bool = False):
        """Obtiene todas las invitaciones de un usuario"""
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return []
        
        query = InvitacionProyecto.query.filter_by(email_destinatario=usuario.email)
        
        if not incluir_expiradas:
            query = query.filter(InvitacionProyecto.estado == 'pendiente')
        
        invitaciones = query.order_by(InvitacionProyecto.fecha_envio.desc()).all()
        
        return [inv.to_dict() for inv in invitaciones]
    
    @staticmethod
    def reenviar_invitacion(invitacion_id: int, admin_usuario_id: int):
        """Reenvía una invitación existente"""
        try:
            invitacion = InvitacionProyecto.query.get(invitacion_id)
            
            if not invitacion:
                return None, "Invitación no encontrada"
            
            # Verificar permisos
            proyecto = Proyecto.query.get(invitacion.proyecto_id)
            
            if proyecto.usuario_id != admin_usuario_id:
                return None, "No tienes permisos para reenviar esta invitación"
            
            # Obtener fecha actual con zona horaria
            now = datetime.now(LOCAL_TZ)
            
            # Asegurarse de que fecha_expiracion tenga zona horaria para comparar
            fecha_exp = invitacion.fecha_expiracion
            if fecha_exp.tzinfo is None:
                fecha_exp = fecha_exp.replace(tzinfo=LOCAL_TZ)
            
            # Extender fecha de expiración si ya expiró
            if fecha_exp <= now:
                invitacion.fecha_expiracion = InvitacionProyecto.crear_fecha_expiracion()
                invitacion.estado = 'pendiente'
            
            invitacion.intentos_reenvio += 1
            invitacion.ultima_fecha_reenvio = now
            
            db.session.commit()
            
            # Reenviar email
            admin = Usuario.query.get(admin_usuario_id)
            email_existe, _ = InvitacionService.verificar_email_existe(invitacion.email_destinatario)
            
            try:
                EmailService.enviar_invitacion_proyecto(
                    email_destinatario=invitacion.email_destinatario,
                    nombre_proyecto=proyecto.nombre,
                    nombre_admin=admin.nombre_completo or admin.username,
                    token=invitacion.token,
                    mensaje_personalizado=invitacion.mensaje_invitacion,
                    es_nuevo_usuario=not email_existe
                )
                print(f"📧 Email de reenvío enviado exitosamente a {invitacion.email_destinatario}")
            except Exception as e:
                print(f"⚠️ Error al enviar email de reenvío: {str(e)}")
                # No fallar si el email no se puede enviar, la invitación ya fue actualizada
            
            return invitacion, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
