"""
Script de prueba para el endpoint de recuperación de contraseña

Este script permite probar el endpoint /forgot-password de forma independiente
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:8000"  # Ajusta según tu configuración
TEST_EMAIL = "test@ejemplo.com"  # Cambia por un email de prueba

async def test_forgot_password():
    """Probar el endpoint de forgot-password"""
    print("🧪 Probando endpoint /forgot-password")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Datos de la solicitud
        request_data = {
            "email": TEST_EMAIL
        }
        
        try:
            # Realizar la petición POST
            response = await client.post(
                f"{API_BASE_URL}/access/forgot-password",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📨 Email de prueba: {TEST_EMAIL}")
            print(f"📊 Status Code: {response.status_code}")
            print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Respuesta exitosa:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("❌ Error en la respuesta:")
                print(f"Status: {response.status_code}")
                print(f"Contenido: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Error de conexión:")
            print("Asegúrate de que el servidor FastAPI esté ejecutándose")
            print("Ejecuta: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")

async def test_validate_reset_token():
    """Probar el endpoint de validación de token"""
    print("\n🧪 Probando endpoint /validate-reset-token")
    print("=" * 50)
    
    # Token de ejemplo (normalmente lo obtendrías del correo)
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
    
    async with httpx.AsyncClient() as client:
        request_data = {
            "token": test_token
        }
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/access/validate-reset-token",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔐 Token de prueba: {test_token[:50]}...")
            print(f"📊 Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Respuesta exitosa:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("❌ Error en la respuesta:")
                print(f"Status: {response.status_code}")
                print(f"Contenido: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Error de conexión:")
            print("Asegúrate de que el servidor FastAPI esté ejecutándose")
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")

async def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas de recuperación de contraseña")
    print("=" * 60)
    
    await test_forgot_password()
    await test_validate_reset_token()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("\n💡 Notas importantes:")
    print("- Asegúrate de configurar las variables de correo en .env")
    print("- El servidor debe estar ejecutándose en el puerto configurado")
    print("- Revisa los logs del servidor para más detalles")

if __name__ == "__main__":
    # Para ejecutar las pruebas:
    # python test_forgot_password.py
    asyncio.run(main())
