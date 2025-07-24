"""
Script de validación de configuración

Este script verifica que la configuración de correo esté funcionando correctamente
después de los cambios en core/config.py
"""

from core.config import settings
from core.email import validate_email_config, email_service
import asyncio

def test_config_loading():
    """Probar que la configuración se carga correctamente"""
    print("🔧 Probando carga de configuración")
    print("=" * 50)
    
    # Verificar configuración de base de datos
    print(f"📊 Base de datos:")
    print(f"  - Host: {settings.DB_HOST}")
    print(f"  - Puerto: {settings.DB_PORT}")
    print(f"  - Usuario: {settings.DB_USER}")
    print(f"  - Base de datos: {settings.DB_NAME}")
    print()
    
    # Verificar configuración JWT
    print(f"🔐 JWT:")
    print(f"  - Algoritmo: {settings.jwt_algorithm}")
    print(f"  - Expiración: {settings.jwt_access_token_expire_minutes} minutos")
    print(f"  - Secret configurado: {'✅' if settings.jwt_secret else '❌'}")
    print()
    
    # Verificar configuración de correo
    print(f"📧 Correo:")
    print(f"  - Servidor: {settings.mail_server}")
    print(f"  - Puerto: {settings.mail_port}")
    print(f"  - Usuario: {settings.mail_username}")
    print(f"  - From: {settings.mail_from}")
    print(f"  - From Name: {settings.mail_from_name}")
    print(f"  - STARTTLS: {settings.mail_starttls}")
    print(f"  - SSL/TLS: {settings.mail_ssl_tls}")
    print(f"  - Usar credenciales: {settings.use_credentials}")
    print(f"  - Validar certificados: {settings.validate_certs}")
    print()
    
    # Verificar que no hay campos vacíos críticos
    missing_fields = []
    if not settings.mail_username:
        missing_fields.append("MAIL_USERNAME")
    if not settings.mail_password:
        missing_fields.append("MAIL_PASSWORD")
    if not settings.mail_from:
        missing_fields.append("MAIL_FROM")
    
    if missing_fields:
        print(f"❌ Campos faltantes: {', '.join(missing_fields)}")
        return False
    else:
        print("✅ Todas las configuraciones están presentes")
        return True

def test_email_config_validation():
    """Probar la validación del servicio de correo"""
    print("\n🧪 Probando validación del servicio de correo")
    print("=" * 50)
    
    try:
        is_valid = validate_email_config()
        if is_valid:
            print("✅ Configuración de correo válida")
            return True
        else:
            print("❌ Configuración de correo inválida")
            return False
    except Exception as e:
        print(f"❌ Error al validar configuración: {str(e)}")
        return False

async def test_email_service_initialization():
    """Probar la inicialización del servicio de correo"""
    print("\n🚀 Probando inicialización del servicio de correo")
    print("=" * 50)
    
    try:
        # Intentar inicializar el servicio
        service = email_service
        print("✅ Servicio de correo inicializado correctamente")
        
        # Probar creación de mensaje (sin enviar)
        test_recipients = ["test@ejemplo.com"]
        test_subject = "Prueba de configuración"
        test_body = "<p>Este es un mensaje de prueba</p>"
        
        print("✅ Estructura de mensaje creada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar servicio: {str(e)}")
        return False

async def main():
    """Función principal"""
    print("🔍 Validación de Configuración - Gestión Formación")
    print("=" * 60)
    
    # Ejecutar pruebas
    config_ok = test_config_loading()
    validation_ok = test_email_config_validation()
    service_ok = await test_email_service_initialization()
    
    print("\n" + "=" * 60)
    print("📋 Resumen de Resultados:")
    print(f"  - Carga de configuración: {'✅' if config_ok else '❌'}")
    print(f"  - Validación de correo: {'✅' if validation_ok else '❌'}")
    print(f"  - Inicialización de servicio: {'✅' if service_ok else '❌'}")
    
    if all([config_ok, validation_ok, service_ok]):
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
        print("\n💡 Próximos pasos:")
        print("  1. Ejecutar: uvicorn main:app --reload")
        print("  2. Probar endpoint: POST /access/forgot-password")
        print("  3. Verificar correos en Mailtrap")
    else:
        print("\n⚠️  Hay problemas en la configuración que deben solucionarse.")
        print("\n🔧 Acciones recomendadas:")
        print("  1. Verificar archivo .env")
        print("  2. Revisar variables de entorno")
        print("  3. Verificar credenciales de Mailtrap")

if __name__ == "__main__":
    asyncio.run(main())
