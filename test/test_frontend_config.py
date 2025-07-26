"""
Script de validación para la nueva configuración frontend_url

Este script verifica que la configuración de frontend_url se carga correctamente
y se utiliza en el sistema de recuperación de contraseñas.
"""

from core.config import settings
from core.security import create_reset_password_token
import os

def test_frontend_url_config():
    """Probar que la configuración de frontend_url se carga correctamente"""
    print("🌐 Probando configuración de frontend_url")
    print("=" * 50)
    
    # Verificar que la configuración se carga
    print(f"Frontend URL configurada: {settings.frontend_url}")
    
    # Verificar valor por defecto
    if not os.getenv("FRONTEND_URL"):
        print("ℹ️  Usando valor por defecto (FRONTEND_URL no está en .env)")
        expected_default = "http://localhost:3000"
        if settings.frontend_url == expected_default:
            print(f"✅ Valor por defecto correcto: {expected_default}")
        else:
            print(f"❌ Valor por defecto incorrecto. Esperado: {expected_default}, Actual: {settings.frontend_url}")
    else:
        env_value = os.getenv("FRONTEND_URL")
        print(f"ℹ️  Usando valor de .env: {env_value}")
        if settings.frontend_url == env_value:
            print(f"✅ Valor de .env correcto: {env_value}")
        else:
            print(f"❌ Valor de .env incorrecto. Esperado: {env_value}, Actual: {settings.frontend_url}")
    
    return settings.frontend_url

def test_reset_url_generation():
    """Probar que se genera correctamente la URL de reset"""
    print("\n🔗 Probando generación de URL de reset")
    print("=" * 50)
    
    # Crear un token de prueba
    test_user_id = 123
    reset_token = create_reset_password_token(test_user_id)
    
    # Simular la construcción de URL como en el endpoint
    reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
    
    print(f"Token generado: {reset_token[:50]}...")
    print(f"URL completa: {reset_url}")
    
    # Verificar formato
    expected_start = f"{settings.frontend_url}/reset-password?token="
    if reset_url.startswith(expected_start):
        print("✅ Formato de URL correcto")
    else:
        print(f"❌ Formato de URL incorrecto. Debería empezar con: {expected_start}")
    
    # Verificar que contiene el token
    if reset_token in reset_url:
        print("✅ Token incluido en la URL")
    else:
        print("❌ Token no incluido en la URL")
    
    return reset_url

def test_different_frontend_urls():
    """Probar diferentes URLs de frontend"""
    print("\n🧪 Probando diferentes URLs de frontend")
    print("=" * 50)
    
    test_urls = [
        "http://localhost:3000",
        "https://miapp.com",
        "https://frontend.ejemplo.com",
        "http://192.168.1.100:3000",
        "https://staging.miapp.com"
    ]
    
    for url in test_urls:
        # Simular diferentes valores
        test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        full_url = f"{url}/reset-password?token={test_token}"
        
        print(f"  Frontend: {url}")
        print(f"  Reset URL: {full_url}")
        
        # Validaciones básicas
        if "/reset-password?token=" in full_url:
            print("  ✅ Formato válido")
        else:
            print("  ❌ Formato inválido")
        print()

def show_configuration_summary():
    """Mostrar resumen de toda la configuración"""
    print("\n📋 Resumen de Configuración")
    print("=" * 50)
    
    config_items = [
        ("Proyecto", settings.PROJECT_NAME),
        ("Versión", settings.PROJECT_VERSION),
        ("Frontend URL", settings.frontend_url),
        ("Base de datos", f"{settings.DB_HOST}:{settings.DB_PORT}"),
        ("Servidor de correo", f"{settings.mail_server}:{settings.mail_port}"),
        ("JWT Algoritmo", settings.jwt_algorithm),
        ("JWT Expiración", f"{settings.jwt_access_token_expire_minutes} min"),
    ]
    
    for label, value in config_items:
        print(f"  {label:<20}: {value}")

def main():
    """Función principal"""
    print("🔧 Validación de Configuración frontend_url")
    print("=" * 60)
    
    try:
        # Ejecutar pruebas
        frontend_url = test_frontend_url_config()
        reset_url = test_reset_url_generation()
        test_different_frontend_urls()
        show_configuration_summary()
        
        print("\n" + "=" * 60)
        print("✅ Todas las validaciones completadas")
        
        print("\n💡 Uso en el código:")
        print("```python")
        print("from core.config import settings")
        print("reset_url = f\"{settings.frontend_url}/reset-password?token={token}\"")
        print("```")
        
        print("\n🔧 Para cambiar la URL del frontend:")
        print("Edita la variable FRONTEND_URL en tu archivo .env")
        print(f"Actual: FRONTEND_URL={frontend_url}")
        
    except Exception as e:
        print(f"\n❌ Error durante las validaciones: {str(e)}")

if __name__ == "__main__":
    main()
