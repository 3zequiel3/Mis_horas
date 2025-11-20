"""
Servicio de envío de emails usando SMTP
Soporta Gmail y otros proveedores SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional
from app.config import (
    SMTP_HOST, 
    SMTP_PORT, 
    SMTP_USE_TLS, 
    SMTP_USER, 
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    APP_URL
)


class EmailService:
    """Servicio para envío de emails"""
    
    @staticmethod
    def _crear_conexion():
        """Crea una conexión SMTP"""
        try:
            servidor = smtplib.SMTP(SMTP_HOST, int(SMTP_PORT))
            servidor.ehlo()
            
            if SMTP_USE_TLS:
                servidor.starttls()
                servidor.ehlo()
            
            servidor.login(SMTP_USER, SMTP_PASSWORD)
            return servidor
        except Exception as e:
            print(f"Error al conectar con SMTP: {str(e)}")
            raise

    @staticmethod
    def enviar_email(
        destinatarios: List[str],
        asunto: str,
        cuerpo_html: str,
        cuerpo_texto: Optional[str] = None,
        adjuntos: Optional[List[str]] = None
    ) -> bool:
        """
        Envía un email
        
        Args:
            destinatarios: Lista de emails destinatarios
            asunto: Asunto del email
            cuerpo_html: Contenido HTML del email
            cuerpo_texto: Contenido en texto plano (opcional)
            adjuntos: Lista de rutas de archivos a adjuntar (opcional)
        
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            # Crear mensaje
            mensaje = MIMEMultipart('alternative')
            mensaje['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
            mensaje['To'] = ', '.join(destinatarios)
            mensaje['Subject'] = asunto
            
            # Agregar cuerpo en texto plano
            if cuerpo_texto:
                parte_texto = MIMEText(cuerpo_texto, 'plain', 'utf-8')
                mensaje.attach(parte_texto)
            
            # Agregar cuerpo HTML
            parte_html = MIMEText(cuerpo_html, 'html', 'utf-8')
            mensaje.attach(parte_html)
            
            # Agregar adjuntos si existen
            if adjuntos:
                for archivo_path in adjuntos:
                    if os.path.exists(archivo_path):
                        with open(archivo_path, 'rb') as archivo:
                            parte = MIMEBase('application', 'octet-stream')
                            parte.set_payload(archivo.read())
                            encoders.encode_base64(parte)
                            parte.add_header(
                                'Content-Disposition',
                                f'attachment; filename={os.path.basename(archivo_path)}'
                            )
                            mensaje.attach(parte)
            
            # Enviar email
            servidor = EmailService._crear_conexion()
            servidor.sendmail(SMTP_FROM_EMAIL, destinatarios, mensaje.as_string())
            servidor.quit()
            
            print(f"Email enviado exitosamente a: {', '.join(destinatarios)}")
            return True
            
        except Exception as e:
            print(f"Error al enviar email: {str(e)}")
            return False

    @staticmethod
    def enviar_invitacion_proyecto(
        email_destinatario: str,
        nombre_proyecto: str,
        nombre_admin: str,
        token: str,
        mensaje_personalizado: Optional[str] = None,
        es_nuevo_usuario: bool = False
    ) -> bool:
        """
        Envía email de invitación a un proyecto
        
        Args:
            email_destinatario: Email del destinatario
            nombre_proyecto: Nombre del proyecto
            nombre_admin: Nombre del administrador que invita
            token: Token de invitación
            mensaje_personalizado: Mensaje personalizado del admin
            es_nuevo_usuario: Si el usuario debe registrarse primero
        
        Returns:
            bool: True si se envió correctamente
        """
        if es_nuevo_usuario:
            url_accion = f"{APP_URL}/register?invitacion={token}"
            titulo_accion = "Crear cuenta y aceptar invitación"
            texto_adicional = "Primero deberás crear tu cuenta en el sistema para luego aceptar la invitación."
        else:
            url_accion = f"{APP_URL}/invitaciones/{token}"
            titulo_accion = "Aceptar invitación"
            texto_adicional = "Puedes revisar los detalles y aceptar o rechazar la invitación desde tu panel."
        
        asunto = f"Invitación al proyecto: {nombre_proyecto}"
        
        # Cuerpo en texto plano
        cuerpo_texto = f"""
Hola,

{nombre_admin} te ha invitado a unirte al proyecto "{nombre_proyecto}" en MisHoras.

{mensaje_personalizado if mensaje_personalizado else ""}

{texto_adicional}

Para aceptar la invitación, ingresa a:
{url_accion}

Este enlace es válido por 7 días.

Saludos,
El equipo de MisHoras
        """
        
        # Cuerpo HTML
        cuerpo_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .button {{ display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        .info-box {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Invitación a Proyecto</h1>
        </div>
        <div class="content">
            <p><strong>{nombre_admin}</strong> te ha invitado a unirte al proyecto:</p>
            
            <div class="info-box">
                <h2 style="margin: 0; color: #667eea;">📋 {nombre_proyecto}</h2>
            </div>
            
            {f'<p><em>"{mensaje_personalizado}"</em></p>' if mensaje_personalizado else ''}
            
            <p>{texto_adicional}</p>
            
            <center>
                <a href="{url_accion}" class="button">{titulo_accion}</a>
            </center>
            
            <p style="font-size: 12px; color: #666; margin-top: 30px;">
                <strong>Nota:</strong> Este enlace es válido por 7 días. Si no puedes hacer clic en el botón, copia y pega el siguiente enlace en tu navegador:
            </p>
            <p style="font-size: 11px; color: #888; word-break: break-all;">
                {url_accion}
            </p>
        </div>
        <div class="footer">
            <p>Este es un email automático de MisHoras - Sistema de Gestión de Horas</p>
            <p>© 2025 MisHoras. Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return EmailService.enviar_email(
            destinatarios=[email_destinatario],
            asunto=asunto,
            cuerpo_html=cuerpo_html,
            cuerpo_texto=cuerpo_texto
        )

    @staticmethod
    def enviar_notificacion_justificacion_aprobada(
        email_empleado: str,
        nombre_empleado: str,
        nombre_proyecto: str,
        horas_justificadas: float,
        comentario_admin: Optional[str] = None
    ) -> bool:
        """Envía notificación de justificación aprobada"""
        asunto = f"Justificación aprobada - {nombre_proyecto}"
        
        cuerpo_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .success-box {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 15px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Justificación Aprobada</h1>
        </div>
        <div class="content">
            <p>Hola <strong>{nombre_empleado}</strong>,</p>
            
            <p>Tu justificación de horas para el proyecto <strong>{nombre_proyecto}</strong> ha sido aprobada.</p>
            
            <div class="success-box">
                <p><strong>Horas justificadas:</strong> {horas_justificadas} horas</p>
            </div>
            
            {f'<p><strong>Comentario del administrador:</strong></p><p><em>{comentario_admin}</em></p>' if comentario_admin else ''}
            
            <p>Las horas han sido actualizadas en tu registro.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return EmailService.enviar_email(
            destinatarios=[email_empleado],
            asunto=asunto,
            cuerpo_html=cuerpo_html
        )

    @staticmethod
    def enviar_recordatorio_marcado(
        email_empleado: str,
        nombre_empleado: str,
        nombre_proyecto: str,
        tipo: str = 'entrada'  # 'entrada' o 'salida'
    ) -> bool:
        """Envía recordatorio para marcar entrada o salida"""
        if tipo == 'entrada':
            emoji = "🌅"
            accion = "marcar tu entrada"
        else:
            emoji = "🌙"
            accion = "marcar tu salida"
        
        asunto = f"Recordatorio: {accion.capitalize()} - {nombre_proyecto}"
        
        cuerpo_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{emoji} Recordatorio</h1>
        </div>
        <p>Hola <strong>{nombre_empleado}</strong>,</p>
        <p>Este es un recordatorio para <strong>{accion}</strong> en el proyecto <strong>{nombre_proyecto}</strong>.</p>
        <p>Ingresa al sistema para registrar tu asistencia.</p>
    </div>
</body>
</html>
        """
        
        return EmailService.enviar_email(
            destinatarios=[email_empleado],
            asunto=asunto,
            cuerpo_html=cuerpo_html
        )
