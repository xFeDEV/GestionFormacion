"""
Script de prueba para el endpoint de reset de contraseña

Este script permite probar el endpoint /reset-password de forma completa
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:8000"  # Ajusta según tu configuración
TEST_EMAIL = "test@ejemplo.com"  # Cambia por un email de prueba válido

async def test_complete_password_reset_flow():
    """Probar el flujo completo de reset de contraseña"""
    print("🔄 Probando flujo completo de reset de contraseña")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Paso 1: Solicitar reset de contraseña
        print("📧 Paso 1: Solicitando reset de contraseña...")
        forgot_request = {"email": TEST_EMAIL}
        
        try:
            forgot_response = await client.post(
                f"{API_BASE_URL}/access/forgot-password",
                json=forgot_request,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {forgot_response.status_code}")
            if forgot_response.status_code == 200:
                print("✅ Solicitud enviada exitosamente")
                forgot_result = forgot_response.json()
                print(f"Mensaje: {forgot_result['message']}")
            else:
                print("❌ Error en solicitud de reset")
                print(f"Respuesta: {forgot_response.text}")
                return
                
        except Exception as e:
            print(f"❌ Error en solicitud: {str(e)}")
            return
        
        print("\n" + "⚠️  NOTA: En un caso real, obtendrías el token del correo electrónico")
        print("Para esta prueba, necesitas un token válido generado previamente.")
        
        # Paso 2: Probar con token inválido
        print("\n🧪 Paso 2: Probando con token inválido...")
        invalid_token = "token_invalido_para_prueba"
        
        reset_request = {
            "token": invalid_token,
            "new_password": "nueva_contraseña_123"
        }
        
        try:
            reset_response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json=reset_request,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {reset_response.status_code}")
            reset_result = reset_response.json()
            
            if reset_response.status_code == 400:
                print("✅ Token inválido rechazado correctamente")
                print(f"Mensaje: {reset_result['detail']}")
            else:
                print("⚠️  Respuesta inesperada")
                print(json.dumps(reset_result, indent=2, ensure_ascii=False))
                
        except Exception as e:
            print(f"❌ Error en reset: {str(e)}")
        
        # Paso 3: Probar validaciones
        print("\n🔍 Paso 3: Probando validaciones...")
        
        # Contraseña muy corta
        short_password_request = {
            "token": "token_cualquiera",
            "new_password": "123"
        }
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json=short_password_request,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Contraseña corta - Status: {response.status_code}")
            if response.status_code == 400:
                result = response.json()
                print(f"✅ Validación de longitud: {result['detail']}")
            
        except Exception as e:
            print(f"❌ Error en validación: {str(e)}")

async def test_reset_password_validations():
    """Probar las validaciones del endpoint"""
    print("\n🔍 Probando validaciones específicas")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Campos vacíos
        print("1. Probando campos vacíos...")
        empty_request = {"token": "", "new_password": ""}
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json=empty_request,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 400:
                result = response.json()
                print(f"   ✅ Validación: {result['detail']}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 2: Solo token vacío
        print("\n2. Probando solo token vacío...")
        token_empty_request = {"token": "", "new_password": "contraseña_válida"}
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json=token_empty_request,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 3: Solo contraseña vacía
        print("\n3. Probando solo contraseña vacía...")
        password_empty_request = {"token": "token_cualquiera", "new_password": ""}
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json=password_empty_request,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def main():
    """Función principal"""
    print("🧪 Pruebas del Endpoint de Reset de Contraseña")
    print("=" * 70)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print(f"📧 Email de prueba: {TEST_EMAIL}")
    print()
    
    try:
        await test_complete_password_reset_flow()
        await test_reset_password_validations()
        
        print("\n" + "=" * 70)
        print("✅ Pruebas completadas")
        print("\n💡 Notas importantes:")
        print("- Para una prueba completa, necesitas un token real del correo")
        print("- Verifica que el servidor esté ejecutándose")
        print("- Revisa los logs del servidor para más detalles")
        print("- Comprueba que la base de datos esté accesible")
        
    except Exception as e:
        print(f"\n❌ Error general en las pruebas: {str(e)}")

if __name__ == "__main__":
    # Para ejecutar las pruebas:
    # python test_reset_password.py
    asyncio.run(main())
