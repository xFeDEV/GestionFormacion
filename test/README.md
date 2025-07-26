# 🧪 Tests - Gestión Formación

Esta carpeta está preparada para contener todos los archivos de prueba del sistema de Gestión Formación.

## 📁 Estado Actual

La carpeta de tests ha sido limpiada y está lista para futuras implementaciones de pruebas.

## 🚀 Desarrollo de Pruebas

Cuando se desarrollen nuevas pruebas, se recomienda seguir esta estructura:

### **Autenticación y Seguridad**
- `test_auth.py` - Pruebas básicas de autenticación
- `test_forgot_password.py` - Pruebas de solicitud de recuperación de contraseña
- `test_reset_password.py` - Pruebas de reset de contraseña

### **Funcionalidades del Sistema**
- `test_usuarios.py` - Pruebas de gestión de usuarios
- `test_grupos.py` - Pruebas de gestión de grupos
- `test_programas.py` - Pruebas de gestión de programas
- `test_centros.py` - Pruebas de centros de formación

### **APIs y Endpoints**
- `test_api_auth.py` - Pruebas de endpoints de autenticación
- `test_api_usuarios.py` - Pruebas de API de usuarios
- `test_api_grupos.py` - Pruebas de API de grupos

## 🚀 Cómo Ejecutar las Pruebas

### **Ejecutar una prueba específica**
```bash
# Desde la raíz del proyecto
python test/test_complete_password_reset_flow.py
```

### **Ejecutar con pytest (si está instalado)**
```bash
pytest test/
```

### **Ejecutar todas las pruebas manualmente**
```bash
python test/test_auth.py
python test/test_config.py
python test/test_forgot_password.py
python test/test_reset_password.py
python test/test_complete_password_reset_flow.py
python test/test_password_changed_at_verification.py
```

## ⚙️ Requisitos para las Pruebas

1. **Servidor ejecutándose**
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Variables de entorno configuradas** (archivo `.env`)
   - Configuración de base de datos
   - Configuración de email (SMTP)
   - Claves de seguridad JWT

3. **Usuario de prueba en la base de datos**
   - Email válido para pruebas de recuperación
   - Permisos adecuados

## 📋 Descripción de Pruebas

### **test_complete_password_reset_flow.py**
- ✅ Flujo completo: solicitud → validación → reset
- ✅ Verificación de invalidación de tokens
- ✅ Casos especiales de seguridad

### **test_password_changed_at_verification.py**
- ✅ Validación de timestamps en tokens
- ✅ Prevención de reutilización de tokens
- ✅ Escenarios de tokens con/sin fecha

### **test_config.py**
- ✅ Validación de configuración de email
- ✅ Verificación de variables de entorno
- ✅ Pruebas de conectividad SMTP

## 🔧 Configuración de Test

```python
# Configuración típica para pruebas
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"  # Cambiar por email válido
```

## 💡 Consejos

- **Ejecutar servidor antes de las pruebas**
- **Verificar logs del servidor** durante las pruebas
- **Usar emails de prueba** válidos en tu base de datos
- **Revisar Mailtrap** para emails enviados
- **Revisar configuración** si las pruebas fallan

## 🚨 Troubleshooting

### Error de conexión
```
❌ Error de conexión - servidor no disponible
```
**Solución:** Asegúrate de que el servidor esté ejecutándose en el puerto 8000

### Error de configuración de email
```
❌ Error: Configuración de correo incompleta
```
**Solución:** Verifica las variables de entorno en tu archivo `.env`

### Token inválido
```
❌ Token inválido o expirado
```
**Solución:** Los tokens expiran en 15 minutos, genera uno nuevo

---

**Ubicación anterior:** Archivos estaban dispersos en la raíz del proyecto  
**Organización actual:** Todos los tests centralizados en `/test/`  
**Fecha de reorganización:** Julio 2025
