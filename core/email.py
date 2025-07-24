import os
from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from jinja2 import Template
from core.config import settings
import asyncio


class EmailSchema(BaseModel):
    email: List[EmailStr]
    subject: str
    body: str
    subtype: MessageType = MessageType.html


class EmailConfig:
    """Configuración para el servicio de correo electrónico"""
    
    def __init__(self):
        # Usar configuración centralizada desde settings
        self.MAIL_USERNAME = settings.mail_username
        self.MAIL_PASSWORD = settings.mail_password
        self.MAIL_FROM = settings.mail_from
        self.MAIL_PORT = settings.mail_port
        self.MAIL_SERVER = settings.mail_server
        self.MAIL_FROM_NAME = settings.mail_from_name
        self.MAIL_STARTTLS = settings.mail_starttls
        self.MAIL_SSL_TLS = settings.mail_ssl_tls
        self.USE_CREDENTIALS = settings.use_credentials
        self.VALIDATE_CERTS = settings.validate_certs

    def get_config(self) -> ConnectionConfig:
        """Retorna la configuración de conexión para FastMail"""
        if not all([self.MAIL_USERNAME, self.MAIL_PASSWORD, self.MAIL_FROM]):
            raise ValueError("Las credenciales de correo no están configuradas correctamente. "
                           "Verifica las variables de entorno MAIL_USERNAME, MAIL_PASSWORD y MAIL_FROM")
        
        return ConnectionConfig(
            MAIL_USERNAME=self.MAIL_USERNAME,
            MAIL_PASSWORD=self.MAIL_PASSWORD,
            MAIL_FROM=self.MAIL_FROM,
            MAIL_PORT=self.MAIL_PORT,
            MAIL_SERVER=self.MAIL_SERVER,
            MAIL_FROM_NAME=self.MAIL_FROM_NAME,
            MAIL_STARTTLS=self.MAIL_STARTTLS,
            MAIL_SSL_TLS=self.MAIL_SSL_TLS,
            USE_CREDENTIALS=self.USE_CREDENTIALS,
            VALIDATE_CERTS=self.VALIDATE_CERTS,
            TEMPLATE_FOLDER="./templates/email"
        )


# Instancia global de configuración
email_config = EmailConfig()
conf = email_config.get_config()


class EmailService:
    """Servicio para el envío de correos electrónicos"""
    
    def __init__(self):
        self.fastmail = FastMail(conf)
    
    async def send_email_async(
        self,
        recipients: List[EmailStr],
        subject: str,
        body: str,
        subtype: MessageType = MessageType.html,
        attachments: List = None
    ) -> bool:
        """
        Envía un correo electrónico de forma asíncrona
        
        Args:
            recipients: Lista de direcciones de correo destinatarias
            subject: Asunto del correo
            body: Cuerpo del mensaje (puede ser HTML o texto plano)
            subtype: Tipo de mensaje (html o plain)
            attachments: Lista de archivos adjuntos (opcional)
        
        Returns:
            bool: True si el correo se envió exitosamente, False en caso contrario
        """
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=subtype,
                attachments=attachments or []
            )
            
            await self.fastmail.send_message(message)
            return True
            
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
            return False
    
    async def send_template_email_async(
        self,
        recipients: List[EmailStr],
        subject: str,
        template_name: str,
        template_data: dict = None,
        attachments: List = None
    ) -> bool:
        """
        Envía un correo electrónico usando una plantilla
        
        Args:
            recipients: Lista de direcciones de correo destinatarias
            subject: Asunto del correo
            template_name: Nombre del archivo de plantilla
            template_data: Datos para renderizar en la plantilla
            attachments: Lista de archivos adjuntos (opcional)
        
        Returns:
            bool: True si el correo se envió exitosamente, False en caso contrario
        """
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                template_body=template_data or {},
                subtype=MessageType.html,
                attachments=attachments or []
            )
            
            await self.fastmail.send_message(message, template_name=template_name)
            return True
            
        except Exception as e:
            print(f"Error al enviar correo con plantilla: {str(e)}")
            return False
    
    async def send_welcome_email(
        self,
        recipient_email: EmailStr,
        recipient_name: str,
        temporary_password: str = None
    ) -> bool:
        """
        Envía un correo de bienvenida a un nuevo usuario
        
        Args:
            recipient_email: Correo del destinatario
            recipient_name: Nombre del destinatario
            temporary_password: Contraseña temporal (opcional)
        
        Returns:
            bool: True si el correo se envió exitosamente, False en caso contrario
        """
        subject = "Bienvenido a Gestión Formación"
        
        if temporary_password:
            body = f"""
            <html>
                <body>
                    <h2>¡Bienvenido a Gestión Formación!</h2>
                    <p>Hola {recipient_name},</p>
                    <p>Tu cuenta ha sido creada exitosamente.</p>
                    <p><strong>Credenciales de acceso:</strong></p>
                    <ul>
                        <li>Usuario: {recipient_email}</li>
                        <li>Contraseña temporal: {temporary_password}</li>
                    </ul>
                    <p><strong>Por seguridad, te recomendamos cambiar tu contraseña en el primer inicio de sesión.</strong></p>
                    <p>¡Esperamos que tengas una excelente experiencia!</p>
                    <br>
                    <p>Saludos,<br>El equipo de Gestión Formación</p>
                </body>
            </html>
            """
        else:
            body = f"""
            <html>
                <body>
                    <h2>¡Bienvenido a Gestión Formación!</h2>
                    <p>Hola {recipient_name},</p>
                    <p>Tu cuenta ha sido creada exitosamente.</p>
                    <p>Ya puedes acceder a la plataforma con las credenciales que configuraste.</p>
                    <p>¡Esperamos que tengas una excelente experiencia!</p>
                    <br>
                    <p>Saludos,<br>El equipo de Gestión Formación</p>
                </body>
            </html>
            """
        
        return await self.send_email_async([recipient_email], subject, body)
    
    async def send_password_reset_email(
        self,
        recipient_email: EmailStr,
        recipient_name: str,
        reset_token: str,
        reset_url: str
    ) -> bool:
        """
        Envía un correo para restablecer contraseña
        
        Args:
            recipient_email: Correo del destinatario
            recipient_name: Nombre del destinatario
            reset_token: Token de restablecimiento
            reset_url: URL base para restablecer contraseña
        
        Returns:
            bool: True si el correo se envió exitosamente, False en caso contrario
        """
        subject = "Restablecimiento de contraseña - Gestión Formación"
        
        full_reset_url = f"{reset_url}?token={reset_token}"
        
        body = f"""
        <html>
            <body>
                <h2>Restablecimiento de contraseña</h2>
                <p>Hola {recipient_name},</p>
                <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
                <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                <p><a href="{full_reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Restablecer contraseña</a></p>
                <p><strong>Este enlace expirará en 24 horas.</strong></p>
                <p>Si no solicitaste este restablecimiento, puedes ignorar este correo.</p>
                <br>
                <p>Saludos,<br>El equipo de Gestión Formación</p>
            </body>
        </html>
        """
        
        return await self.send_email_async([recipient_email], subject, body)


# Instancia global del servicio de correo
email_service = EmailService()


# Función de conveniencia para envío rápido
async def send_email_async(
    recipients: List[EmailStr],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html
) -> bool:
    """
    Función de conveniencia para enviar correos de forma asíncrona
    
    Args:
        recipients: Lista de direcciones de correo destinatarias
        subject: Asunto del correo
        body: Cuerpo del mensaje
        subtype: Tipo de mensaje (html o plain)
    
    Returns:
        bool: True si el correo se envió exitosamente, False en caso contrario
    """
    return await email_service.send_email_async(recipients, subject, body, subtype)


# Función para validar configuración
def validate_email_config() -> bool:
    """
    Valida que la configuración de correo esté completa
    
    Returns:
        bool: True si la configuración es válida, False en caso contrario
    """
    try:
        email_config.get_config()
        return True
    except ValueError:
        return False
