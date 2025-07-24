"""
Ejemplo de uso del servicio de correo electrónico

Este archivo muestra cómo utilizar el servicio de correo configurado
en core/email.py para diferentes casos de uso.
"""

import asyncio
from typing import List
from pydantic import EmailStr
from core.email import email_service, send_email_async, validate_email_config


async def ejemplo_correo_simple():
    """Ejemplo de envío de correo simple"""
    recipients = ["usuario@ejemplo.com"]
    subject = "Correo de prueba"
    body = """
    <html>
        <body>
            <h2>Correo de prueba</h2>
            <p>Este es un correo de prueba enviado desde Gestión Formación.</p>
        </body>
    </html>
    """
    
    success = await send_email_async(recipients, subject, body)
    if success:
        print("✅ Correo enviado exitosamente")
    else:
        print("❌ Error al enviar correo")


async def ejemplo_correo_bienvenida():
    """Ejemplo de correo de bienvenida"""
    recipient_email = "nuevo_usuario@ejemplo.com"
    recipient_name = "Juan Pérez"
    temporary_password = "temp123456"
    
    success = await email_service.send_welcome_email(
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        temporary_password=temporary_password
    )
    
    if success:
        print("✅ Correo de bienvenida enviado exitosamente")
    else:
        print("❌ Error al enviar correo de bienvenida")


async def ejemplo_correo_recuperacion():
    """Ejemplo de correo de recuperación de contraseña"""
    recipient_email = "usuario@ejemplo.com"
    recipient_name = "Juan Pérez"
    reset_token = "abc123def456ghi789"
    reset_url = "https://gestionformacion.com/reset-password"
    
    success = await email_service.send_password_reset_email(
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        reset_token=reset_token,
        reset_url=reset_url
    )
    
    if success:
        print("✅ Correo de recuperación enviado exitosamente")
    else:
        print("❌ Error al enviar correo de recuperación")


async def ejemplo_correo_con_plantilla():
    """Ejemplo de correo usando plantilla"""
    recipients = ["usuario@ejemplo.com"]
    subject = "Notificación importante"
    template_name = "base.html"
    template_data = {
        "title": "Notificación importante",
        "name": "Juan Pérez",
        "message": "Te informamos sobre una actualización importante en tu cuenta.",
        "action_url": "https://gestionformacion.com/login",
        "action_text": "Acceder ahora",
        "additional_info": "Si tienes alguna pregunta, no dudes en contactarnos."
    }
    
    success = await email_service.send_template_email_async(
        recipients=recipients,
        subject=subject,
        template_name=template_name,
        template_data=template_data
    )
    
    if success:
        print("✅ Correo con plantilla enviado exitosamente")
    else:
        print("❌ Error al enviar correo con plantilla")


async def main():
    """Función principal para ejecutar ejemplos"""
    print("📧 Ejemplos de uso del servicio de correo electrónico")
    print("=" * 50)
    
    # Validar configuración
    if not validate_email_config():
        print("❌ Error: Configuración de correo incompleta.")
        print("Verifica las variables de entorno en tu archivo .env")
        return
    
    print("✅ Configuración de correo válida")
    print()
    
    # Ejecutar ejemplos (comentar/descomentar según necesidad)
    
    # await ejemplo_correo_simple()
    # await ejemplo_correo_bienvenida()
    # await ejemplo_correo_recuperacion()
    # await ejemplo_correo_con_plantilla()
    
    print("✅ Ejemplos completados")


if __name__ == "__main__":
    # Para ejecutar este archivo directamente:
    # python ejemplo_email.py
    asyncio.run(main())
