# Configuración del Servicio de Correo Electrónico

Este documento explica cómo configurar y usar el servicio de correo electrónico en la aplicación Gestión Formación.

## 📋 Requisitos

- Python 3.8+
- FastAPI
- fastapi-mail
- Variables de entorno configuradas

## 🚀 Instalación

Las dependencias se instalan automáticamente con:

```bash
pip install -r requirements.txt
```

Las dependencias relacionadas con correo incluyen:
- `fastapi-mail==1.4.1`
- `jinja2==3.1.4`
- `aiofiles==23.2.1`

## ⚙️ Configuración

### Variables de Entorno

Configura las siguientes variables en tu archivo `.env`:

```env
# Configuración de correo electrónico
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_FROM=tu_email@gmail.com
MAIL_FROM_NAME=Gestión Formación
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
VALIDATE_CERTS=True
```

### Configuración para Gmail

Para usar Gmail como proveedor de correo:

1. **Habilitar autenticación de 2 factores** en tu cuenta de Gmail
2. **Generar una contraseña de aplicación**:
   - Ve a tu cuenta de Google
   - Seguridad → Contraseñas de aplicaciones
   - Genera una nueva contraseña para "Mail"
   - Usa esta contraseña en `MAIL_PASSWORD`

### Otros Proveedores

#### Outlook/Hotmail
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

#### Yahoo
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

## 📧 Uso Básico

### Importar el Servicio

```python
from core.email import email_service, send_email_async
```

### Envío Simple

```python
import asyncio
from pydantic import EmailStr

async def enviar_correo():
    recipients = ["destinatario@ejemplo.com"]
    subject = "Asunto del correo"
    body = "<h1>Hola mundo!</h1><p>Este es un correo de prueba.</p>"
    
    success = await send_email_async(recipients, subject, body)
    return success

# Ejecutar
asyncio.run(enviar_correo())
```

### Usando el Servicio Completo

```python
from core.email import email_service

async def enviar_con_servicio():
    success = await email_service.send_email_async(
        recipients=["usuario@ejemplo.com"],
        subject="Notificación",
        body="<p>Contenido del mensaje</p>"
    )
    return success
```

## 🎨 Plantillas de Correo

### Usando Plantillas HTML

```python
await email_service.send_template_email_async(
    recipients=["usuario@ejemplo.com"],
    subject="Bienvenido",
    template_name="base.html",
    template_data={
        "title": "¡Bienvenido!",
        "name": "Juan Pérez",
        "message": "Tu cuenta ha sido creada exitosamente.",
        "action_url": "https://ejemplo.com/login",
        "action_text": "Iniciar sesión"
    }
)
```

### Estructura de Plantillas

Las plantillas se ubican en `templates/email/`. Ejemplo de variables disponibles:

- `{{title}}` - Título del correo
- `{{name}}` - Nombre del destinatario
- `{{message}}` - Mensaje principal
- `{{action_url}}` - URL del botón de acción
- `{{action_text}}` - Texto del botón
- `{{credentials}}` - Objeto con credenciales de usuario

## 🛠️ Funciones Predefinidas

### Correo de Bienvenida

```python
await email_service.send_welcome_email(
    recipient_email="nuevo@ejemplo.com",
    recipient_name="Juan Pérez",
    temporary_password="temp123"  # Opcional
)
```

### Recuperación de Contraseña

```python
await email_service.send_password_reset_email(
    recipient_email="usuario@ejemplo.com",
    recipient_name="Juan Pérez",
    reset_token="token123",
    reset_url="https://ejemplo.com/reset"
)
```

## 🔍 Validación y Debugging

### Verificar Configuración

```python
from core.email import validate_email_config

if validate_email_config():
    print("✅ Configuración válida")
else:
    print("❌ Configuración incompleta")
```

### Manejo de Errores

```python
try:
    success = await email_service.send_email_async(
        recipients=["test@ejemplo.com"],
        subject="Prueba",
        body="Contenido"
    )
    if success:
        print("Correo enviado exitosamente")
    else:
        print("Error al enviar correo")
except Exception as e:
    print(f"Error: {e}")
```

## 🚨 Solución de Problemas

### Error de Autenticación
- Verifica que `MAIL_USERNAME` y `MAIL_PASSWORD` sean correctos
- Para Gmail, usa una contraseña de aplicación, no la contraseña normal
- Asegúrate de que la autenticación de 2 factores esté habilitada

### Error de Conexión
- Verifica `MAIL_SERVER` y `MAIL_PORT`
- Confirma que `MAIL_STARTTLS` esté configurado correctamente
- Revisa la conexión a Internet

### Variables de Entorno No Encontradas
- Asegúrate de que el archivo `.env` esté en la raíz del proyecto
- Verifica que las variables estén escritas correctamente
- Reinicia la aplicación después de cambiar las variables

## 📝 Ejemplos Completos

Ejecuta el archivo de ejemplos:

```bash
python ejemplo_email.py
```

Este archivo contiene ejemplos de todos los tipos de correos disponibles.

## 🔐 Seguridad

- **Nunca** hardcodees credenciales en el código
- Usa variables de entorno para información sensible
- Considera usar servicios como SendGrid o AWS SES para producción
- Implementa rate limiting para prevenir spam
- Valida siempre las direcciones de correo antes de enviar

## 📊 Monitoreo

Para producción, considera implementar:
- Logs de envío de correos
- Métricas de entrega
- Manejo de bounces y quejas
- Cola de correos para alto volumen
