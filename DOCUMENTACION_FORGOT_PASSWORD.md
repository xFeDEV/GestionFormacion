# API de Recuperación de Contraseña

Documentación completa del endpoint de recuperación de contraseña implementado en el sistema de Gestión Formación.

## 📚 Endpoints Disponibles

### 1. Solicitar Recuperación de Contraseña

**POST** `/access/forgot-password`

Permite a un usuario solicitar un enlace de recuperación de contraseña.

#### Request Body
```json
{
  "email": "usuario@ejemplo.com"
}
```

#### Response
```json
{
  "message": "Si el correo electrónico está registrado, recibirás un enlace de recuperación."
}
```

#### Características de Seguridad
- ✅ **No revela información**: Siempre devuelve el mismo mensaje, independientemente de si el email existe
- ✅ **Token temporal**: El enlace expira en 15 minutos
- ✅ **Token específico**: Incluye tipo "password_reset" para validación adicional
- ✅ **Logging seguro**: Registra intentos sin exponer información sensible

#### Ejemplo de uso con cURL
```bash
curl -X POST "http://localhost:8000/access/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@ejemplo.com"}'
```

#### Ejemplo de uso con JavaScript
```javascript
const response = await fetch('/access/forgot-password', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'usuario@ejemplo.com'
  })
});

const result = await response.json();
console.log(result.message);
```

### 2. Validar Token de Recuperación

**POST** `/access/validate-reset-token`

Valida si un token de recuperación es válido y no ha expirado.

#### Request Body
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response - Token Válido
```json
{
  "valid": true,
  "message": "Token válido"
}
```

#### Response - Token Inválido
```json
{
  "valid": false,
  "message": "Token inválido o expirado"
}
```

#### Ejemplo de uso con JavaScript
```javascript
const response = await fetch('/access/validate-reset-token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    token: tokenFromURL
  })
});

const result = await response.json();
if (result.valid) {
  // Mostrar formulario de nueva contraseña
} else {
  // Mostrar mensaje de error
}
```

### 3. Restablecer Contraseña

**POST** `/access/reset-password`

Restablece la contraseña del usuario usando un token válido.

#### Request Body
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "nueva_contraseña_segura123"
}
```

#### Response - Éxito
```json
{
  "message": "Contraseña actualizada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.",
  "success": true
}
```

#### Response - Error
```json
{
  "detail": "Token inválido o expirado. Solicita un nuevo enlace de recuperación."
}
```

#### Validaciones Implementadas
- ✅ **Token requerido**: Debe proporcionar un token válido
- ✅ **Contraseña requerida**: Debe proporcionar una nueva contraseña
- ✅ **Longitud mínima**: La contraseña debe tener al menos 6 caracteres
- ✅ **Token válido**: Debe ser un token de recuperación no expirado
- ✅ **Usuario existente**: El usuario del token debe existir en la base de datos

#### Ejemplo de uso con JavaScript
```javascript
const response = await fetch('/access/reset-password', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    token: tokenFromURL,
    new_password: newPasswordFromForm
  })
});

const result = await response.json();
if (response.ok) {
  alert('Contraseña actualizada exitosamente');
  // Redirigir al login
} else {
  alert(result.detail);
}
```

## 📧 Formato del Correo Enviado

### Asunto
"Recuperación de contraseña - Gestión Formación"

### Contenido
El correo incluye:
- Saludo personalizado con el nombre del usuario
- Enlace de recuperación con token único
- Información sobre la expiración (15 minutos)
- Enlace alternativo en texto plano
- Diseño responsive y profesional

### Ejemplo de enlace generado
```
http://localhost:3000/reset-password?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🔐 Seguridad del Token

### Estructura del Token JWT
```json
{
  "sub": "123",           // ID del usuario
  "type": "password_reset", // Tipo específico del token
  "exp": 1640995200       // Expiración (timestamp)
}
```

### Validaciones Implementadas
1. **Firma válida**: Verificada con la clave secreta del sistema
2. **No expirado**: Máximo 15 minutos de validez
3. **Tipo correcto**: Debe ser "password_reset"
4. **Usuario válido**: ID debe corresponder a un usuario existente

## 🚀 Integración con Frontend

### Flujo Recomendado

1. **Formulario de recuperación**
   ```html
   <form id="forgot-password-form">
     <input type="email" name="email" required>
     <button type="submit">Enviar enlace de recuperación</button>
   </form>
   ```

2. **Procesar respuesta**
   ```javascript
   document.getElementById('forgot-password-form').addEventListener('submit', async (e) => {
     e.preventDefault();
     const formData = new FormData(e.target);
     
     const response = await fetch('/access/forgot-password', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ email: formData.get('email') })
     });
     
     const result = await response.json();
     alert(result.message);
   });
   ```

4. **Formulario de nueva contraseña**
   ```javascript
   // En la página /reset-password después de validar token
   document.getElementById('reset-form').addEventListener('submit', async (e) => {
     e.preventDefault();
     const formData = new FormData(e.target);
     const token = new URLSearchParams(window.location.search).get('token');
     
     const response = await fetch('/access/reset-password', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
         token: token,
         new_password: formData.get('new_password')
       })
     });
     
     const result = await response.json();
     if (response.ok) {
       alert('Contraseña actualizada exitosamente');
       window.location.href = '/login';
     } else {
       alert(result.detail);
     }
   });
   ```

3. **Página de recuperación**
   ```javascript
   // En la página /reset-password
   const urlParams = new URLSearchParams(window.location.search);
   const token = urlParams.get('token');
   
   if (token) {
     // Validar token antes de mostrar formulario
     const validation = await fetch('/access/validate-reset-token', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ token })
     });
     
     const result = await validation.json();
     if (result.valid) {
       // Mostrar formulario de nueva contraseña
       showResetForm(token);
     } else {
       // Mostrar error
       showError('El enlace ha expirado o es inválido');
     }
   }
   ```

## 🔧 Configuración Requerida

### Variables de Entorno (.env)
```env
# Configuración de correo
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_FROM=tu_correo@gmail.com
MAIL_FROM_NAME=Gestión Formación
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
VALIDATE_CERTS=True

# JWT
JWT_SECRET=tu_jwt_secret
JWT_ALGORITHM=HS256
```

### Dependencias (requirements.txt)
```
fastapi-mail==1.5.0
jinja2==3.1.4
aiofiles==23.2.1
```

## 🐛 Troubleshooting

### Error común: "Configuración de correo incompleta"
**Solución**: Verificar que todas las variables de entorno estén configuradas correctamente.

### Error común: "Error al enviar correo"
**Posibles causas**:
- Credenciales de correo incorrectas
- Contraseña de aplicación no configurada (Gmail)
- Firewall bloqueando conexiones SMTP
- Configuración SMTP incorrecta

### Error común: "Token inválido o expirado"
**Posibles causas**:
- Token expirado (>15 minutos)
- Token malformado
- Clave JWT incorrecta
- Token de tipo incorrecto

## 📊 Logs y Monitoreo

### Eventos Registrados
- Solicitudes de recuperación (con email, sin revelar existencia)
- Envíos de correo exitosos/fallidos
- Validaciones de token
- Errores del sistema

### Ejemplo de logs
```
INFO - Correo de recuperación enviado a: usuario@ejemplo.com
INFO - Intento de recuperación para email no registrado: noexiste@ejemplo.com
ERROR - Error al enviar correo de recuperación a: usuario@ejemplo.com
```

## ⚡ Optimizaciones para Producción

1. **Cola de correos**: Implementar cola asíncrona para envío masivo
2. **Rate limiting**: Limitar solicitudes por IP/usuario
3. **Métricas**: Implementar métricas de entrega y apertura
4. **CDN para assets**: Usar CDN para imágenes del correo
5. **Servicio externo**: Considerar SendGrid, AWS SES para mayor confiabilidad

## 🧪 Testing

### Pruebas Unitarias
```python
import pytest
from app.api.auth import forgot_password
from core.security import create_reset_password_token, verify_reset_password_token

def test_create_reset_token():
    token = create_reset_password_token(user_id=1)
    assert token is not None
    
def test_verify_reset_token():
    token = create_reset_password_token(user_id=1)
    data = verify_reset_password_token(token)
    assert data["user_id"] == 1
    assert data["type"] == "password_reset"
```

### Pruebas de Integración
```bash
# Ejecutar el script de prueba
python test_forgot_password.py
```

Este endpoint está listo para usar y cumple con las mejores prácticas de seguridad para recuperación de contraseñas.
