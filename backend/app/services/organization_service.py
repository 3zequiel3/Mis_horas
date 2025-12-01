"""
Servicio de gestión de organizaciones y membresías
Lógica de negocio para el sistema multi-tenant
"""

from app import db
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from sqlalchemy import func, and_
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple

LOCAL_TZ = timezone(timedelta(hours=-3))

class OrganizationService:
    """Servicio para gestión de organizaciones"""
    
    @staticmethod
    def crear_organizacion(
        nombre: str,
        owner_id: int,
        descripcion: str = None,
        tipo_organizacion: str = 'personal',
        logo_url: str = None
    ) -> Organization:
        """
        Crea una nueva organización y automáticamente agrega al creador como owner
        """
        # Generar slug único
        slug = Organization.generar_slug(nombre)
        
        # Crear organización
        org = Organization(
            nombre=nombre,
            slug=slug,
            descripcion=descripcion,
            owner_id=owner_id,
            tipo_organizacion=tipo_organizacion,
            logo_url=logo_url,
            activa=True
        )
        
        db.session.add(org)
        db.session.flush()  # Para obtener el ID sin commitear
        
        # Crear membresía automática del owner
        membership = OrganizationMember(
            user_id=owner_id,
            organization_id=org.id,
            role='owner',
            estado='activo',
            fecha_ingreso=datetime.now(LOCAL_TZ)
        )
        
        db.session.add(membership)
        db.session.commit()
        
        return org
    
    @staticmethod
    def crear_organizacion_personal_usuario(user_id: int) -> Organization:
        """
        Crea la organización personal de un usuario nuevo
        Llamar automáticamente al registrarse
        """
        usuario = Usuario.query.get(user_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")
        
        nombre = f"Espacio Personal de {usuario.nombre_completo or usuario.username}"
        
        return OrganizationService.crear_organizacion(
            nombre=nombre,
            owner_id=user_id,
            descripcion="Mi espacio de trabajo personal",
            tipo_organizacion='personal'
        )
    
    @staticmethod
    def obtener_organizaciones_usuario(user_id: int) -> List[Organization]:
        """
        Obtiene todas las organizaciones a las que pertenece un usuario
        Para el selector de contexto
        """
        memberships = OrganizationMember.query.filter_by(
            user_id=user_id,
            estado='activo'
        ).all()
        
        organizations = [m.organization for m in memberships if m.organization.activa]
        
        # Ordenar: Personal primero, luego por fecha de creación
        organizations.sort(
            key=lambda o: (o.tipo_organizacion != 'personal', o.fecha_creacion)
        )
        
        return organizations
    
    @staticmethod
    def obtener_organizacion(org_id: int) -> Optional[Organization]:
        """Obtiene una organización por ID"""
        return Organization.query.filter_by(id=org_id, activa=True).first()
    
    @staticmethod
    def actualizar_organizacion(
        org_id: int,
        nombre: str = None,
        descripcion: str = None,
        logo_url: str = None,
        zona_horaria: str = None,
        moneda: str = None
    ) -> Organization:
        """Actualiza datos de una organización"""
        org = Organization.query.get(org_id)
        if not org:
            raise ValueError("Organización no encontrada")
        
        if nombre:
            org.nombre = nombre
            org.slug = Organization.generar_slug(nombre)
        if descripcion is not None:
            org.descripcion = descripcion
        if logo_url is not None:
            org.logo_url = logo_url
        if zona_horaria:
            org.zona_horaria = zona_horaria
        if moneda:
            org.moneda = moneda
        
        db.session.commit()
        return org
    
    @staticmethod
    def eliminar_organizacion(org_id: int, user_id: int) -> bool:
        """
        Elimina una organización (solo el owner puede hacerlo)
        Soft delete: marca como inactiva
        """
        org = Organization.query.get(org_id)
        if not org:
            raise ValueError("Organización no encontrada")
        
        if org.owner_id != user_id:
            raise PermissionError("Solo el dueño puede eliminar la organización")
        
        # Verificar que no tenga proyectos activos
        proyectos_activos = Proyecto.query.filter_by(
            organization_id=org_id,
            activo=True
        ).count()
        
        if proyectos_activos > 0:
            raise ValueError(
                f"No se puede eliminar. La organización tiene {proyectos_activos} proyectos activos"
            )
        
        org.activa = False
        db.session.commit()
        return True
    
    @staticmethod
    def obtener_miembros(org_id: int) -> List[OrganizationMember]:
        """Obtiene todos los miembros activos de una organización"""
        return OrganizationMember.query.filter_by(
            organization_id=org_id,
            estado='activo'
        ).order_by(
            # Owner primero, luego por rol y fecha de ingreso
            db.case(
                (OrganizationMember.role == 'owner', 0),
                (OrganizationMember.role == 'admin', 1),
                (OrganizationMember.role == 'manager', 2),
                (OrganizationMember.role == 'member', 3),
                (OrganizationMember.role == 'viewer', 4),
                else_=5
            ),
            OrganizationMember.fecha_ingreso.desc()
        ).all()
    
    @staticmethod
    def invitar_miembro(
        org_id: int,
        email: str,
        role: str,
        invitado_por_id: int
    ) -> Tuple[OrganizationMember, bool]:
        """
        Invita a un usuario a una organización por email
        
        Returns:
            (membership, es_nuevo_usuario)
        """
        # Verificar que el invitador tenga permisos
        invitador_membership = OrganizationMember.query.filter_by(
            user_id=invitado_por_id,
            organization_id=org_id,
            estado='activo'
        ).first()
        
        if not invitador_membership or invitador_membership.role not in ['owner', 'admin']:
            raise PermissionError("No tienes permisos para invitar miembros")
        
        # Buscar si el usuario existe
        usuario = Usuario.query.filter_by(email=email).first()
        es_nuevo_usuario = usuario is None
        
        if usuario:
            # Usuario existente - verificar que no sea miembro ya
            membership_existente = OrganizationMember.query.filter_by(
                user_id=usuario.id,
                organization_id=org_id
            ).first()
            
            if membership_existente:
                if membership_existente.estado == 'activo':
                    raise ValueError("El usuario ya es miembro de esta organización")
                elif membership_existente.estado == 'suspendido':
                    # Reactivar membresía
                    membership_existente.estado = 'activo'
                    membership_existente.role = role
                    membership_existente.fecha_ingreso = datetime.now(LOCAL_TZ)
                    db.session.commit()
                    return membership_existente, False
            
            # Crear membresía directa (usuario existente acepta automáticamente)
            membership = OrganizationMember(
                user_id=usuario.id,
                organization_id=org_id,
                role=role,
                estado='activo',
                invitado_por_id=invitado_por_id,
                fecha_invitacion=datetime.now(LOCAL_TZ),
                fecha_aceptacion=datetime.now(LOCAL_TZ),
                fecha_ingreso=datetime.now(LOCAL_TZ)
            )
        else:
            # Usuario nuevo - crear invitación pendiente
            token = OrganizationMember.generar_token_invitacion()
            membership = OrganizationMember(
                user_id=None,  # Se llenará cuando acepte
                organization_id=org_id,
                role=role,
                estado='invitado',
                invitado_por_id=invitado_por_id,
                token_invitacion=token,
                fecha_invitacion=datetime.now(LOCAL_TZ)
            )
            # TODO: Enviar email con el token
        
        db.session.add(membership)
        db.session.commit()
        
        return membership, es_nuevo_usuario
    
    @staticmethod
    def aceptar_invitacion(token: str, user_id: int) -> OrganizationMember:
        """
        Acepta una invitación pendiente
        Llamar después de que un usuario nuevo se registre
        """
        membership = OrganizationMember.query.filter_by(
            token_invitacion=token,
            estado='invitado'
        ).first()
        
        if not membership:
            raise ValueError("Invitación inválida o expirada")
        
        membership.user_id = user_id
        membership.estado = 'activo'
        membership.fecha_aceptacion = datetime.now(LOCAL_TZ)
        membership.fecha_ingreso = datetime.now(LOCAL_TZ)
        membership.token_invitacion = None  # Limpiar token
        
        db.session.commit()
        return membership
    
    @staticmethod
    def remover_miembro(org_id: int, user_id: int, removido_por_id: int) -> bool:
        """
        Remueve un miembro de una organización
        Solo owners y admins pueden remover
        """
        # Verificar permisos del removedor
        removedor_membership = OrganizationMember.query.filter_by(
            user_id=removido_por_id,
            organization_id=org_id,
            estado='activo'
        ).first()
        
        if not removedor_membership or removedor_membership.role not in ['owner', 'admin']:
            raise PermissionError("No tienes permisos para remover miembros")
        
        # No se puede remover al owner
        org = Organization.query.get(org_id)
        if org.owner_id == user_id:
            raise ValueError("No se puede remover al dueño de la organización")
        
        # Remover membresía
        membership = OrganizationMember.query.filter_by(
            user_id=user_id,
            organization_id=org_id
        ).first()
        
        if not membership:
            raise ValueError("El usuario no es miembro de esta organización")
        
        membership.estado = 'suspendido'
        membership.fecha_salida = datetime.now(LOCAL_TZ)
        
        db.session.commit()
        return True
    
    @staticmethod
    def cambiar_rol(
        org_id: int,
        user_id: int,
        nuevo_rol: str,
        cambiado_por_id: int
    ) -> OrganizationMember:
        """Cambia el rol de un miembro (solo owners)"""
        # Verificar que quien cambia sea owner
        cambiador_membership = OrganizationMember.query.filter_by(
            user_id=cambiado_por_id,
            organization_id=org_id,
            estado='activo'
        ).first()
        
        if not cambiador_membership or cambiador_membership.role != 'owner':
            raise PermissionError("Solo el owner puede cambiar roles")
        
        # No se puede cambiar el rol del owner
        org = Organization.query.get(org_id)
        if org.owner_id == user_id:
            raise ValueError("No se puede cambiar el rol del dueño")
        
        membership = OrganizationMember.query.filter_by(
            user_id=user_id,
            organization_id=org_id,
            estado='activo'
        ).first()
        
        if not membership:
            raise ValueError("Miembro no encontrado")
        
        membership.role = nuevo_rol
        db.session.commit()
        
        return membership
    
    @staticmethod
    def verificar_acceso(user_id: int, org_id: int) -> bool:
        """Verifica si un usuario tiene acceso a una organización"""
        membership = OrganizationMember.query.filter_by(
            user_id=user_id,
            organization_id=org_id,
            estado='activo'
        ).first()
        
        return membership is not None
    
    @staticmethod
    def obtener_estadisticas(org_id: int) -> dict:
        """Obtiene estadísticas de una organización"""
        org = Organization.query.get(org_id)
        if not org:
            raise ValueError("Organización no encontrada")
        
        total_miembros = OrganizationMember.query.filter_by(
            organization_id=org_id,
            estado='activo'
        ).count()
        
        total_proyectos = Proyecto.query.filter_by(
            organization_id=org_id
        ).count()
        
        proyectos_activos = Proyecto.query.filter_by(
            organization_id=org_id,
            activo=True
        ).count()
        
        return {
            'total_miembros': total_miembros,
            'total_proyectos': total_proyectos,
            'proyectos_activos': proyectos_activos,
            'plan': org.plan_type,
            'limite_proyectos': org.limite_proyectos,
            'limite_miembros': org.limite_miembros,
        }
