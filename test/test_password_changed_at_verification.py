"""
Script de prueba para la verificación de password_changed_at en reset-password

Este script simula diferentes escenarios para verificar que la lógica de 
verificación del campo password_changed_at funciona correctamente.
"""

import asyncio
import httpx
import json
from datetime import datetime
from core.security import create_reset_password_token

# Configuración
API_BASE_URL = "http://localhost:8000"

async def test_reset_with_valid_token():
    """Probar reset con token válido (fechas coinciden)"""
    print("🧪 Test 1: Reset con token válido (fechas coinciden)")
    print("=" * 60)
    
    # Este test requiere un usuario real en la base de datos
    # y un token generado con la fecha correcta
    
    print("ℹ️  Este test requiere:")
    print("  - Un usuario existente en la base de datos")
    print("  - Un token generado con la fecha password_changed_at correcta")
    print("  - El servidor ejecutándose")
    print()
    
    # Ejemplo de token que incluye password_changed_at
    test_user_id = 1
    test_password_changed_at = datetime.now()
    
    token = create_reset_password_token(
        user_id=test_user_id,
        expire_minutes=15,
        password_changed_at=test_password_changed_at
    )
    
    print(f"Token generado: {token[:50]}...")
    print(f"User ID: {test_user_id}")
    print(f"Password changed at: {test_password_changed_at}")
    print()
    
    async with httpx.AsyncClient() as client:
        request_data = {
            "token": token,
            "new_password": "nueva_contraseña_123"
        }
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            
            if response.status_code == 200:
                print("✅ Reset exitoso")
                print(f"Mensaje: {result.get('message')}")
            elif response.status_code == 400:
                print("⚠️  Reset rechazado (esperado si las fechas no coinciden)")
                print(f"Error: {result.get('detail')}")
            else:
                print(f"❌ Error inesperado: {response.status_code}")
                print(f"Respuesta: {result}")
                
        except httpx.ConnectError:
            print("❌ Error de conexión - asegúrate de que el servidor esté ejecutándose")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def test_reset_with_invalid_token():
    """Probar reset con token que tiene fecha incorrecta"""
    print("\n🧪 Test 2: Reset con token de fecha incorrecta")
    print("=" * 60)
    
    # Generar token con fecha diferente a la de la base de datos
    test_user_id = 1
    wrong_date = datetime(2024, 1, 1, 10, 0, 0)  # Fecha obviamente incorrecta
    
    token = create_reset_password_token(
        user_id=test_user_id,
        expire_minutes=15,
        password_changed_at=wrong_date
    )
    
    print(f"Token con fecha incorrecta: {token[:50]}...")
    print(f"User ID: {test_user_id}")
    print(f"Fecha incorrecta en token: {wrong_date}")
    print()
    
    async with httpx.AsyncClient() as client:
        request_data = {
            "token": token,
            "new_password": "nueva_contraseña_123"
        }
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            
            if response.status_code == 400:
                print("✅ Reset rechazado correctamente")
                print(f"Error: {result.get('detail')}")
                
                # Verificar que el mensaje sea específico sobre contraseña ya cambiada
                if "contraseña ya fue cambiada" in result.get('detail', ''):
                    print("✅ Mensaje de error correcto")
                else:
                    print("⚠️  Mensaje de error no específico")
            else:
                print(f"❌ Respuesta inesperada: {response.status_code}")
                print(f"Debería haber sido rechazado con 400")
                
        except httpx.ConnectError:
            print("❌ Error de conexión - asegúrate de que el servidor esté ejecutándose")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def test_reset_with_no_date_token():
    """Probar reset con token sin fecha"""
    print("\n🧪 Test 3: Reset con token sin fecha")
    print("=" * 60)
    
    test_user_id = 1
    
    # Token sin password_changed_at
    token = create_reset_password_token(
        user_id=test_user_id,
        expire_minutes=15
        # password_changed_at no se proporciona
    )
    
    print(f"Token sin fecha: {token[:50]}...")
    print(f"User ID: {test_user_id}")
    print("Password changed at: None")
    print()
    
    async with httpx.AsyncClient() as client:
        request_data = {
            "token": token,
            "new_password": "nueva_contraseña_123"
        }
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            
            print(f"Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # El resultado depende de si el usuario tiene password_changed_at en la DB
            if response.status_code == 200:
                print("✅ Reset exitoso (usuario sin password_changed_at previo)")
            elif response.status_code == 400:
                print("✅ Reset rechazado (usuario ya tiene password_changed_at)")
            else:
                print(f"⚠️  Respuesta inesperada: {response.status_code}")
                
        except httpx.ConnectError:
            print("❌ Error de conexión - asegúrate de que el servidor esté ejecutándose")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def main():
    """Función principal"""
    print("🔐 Pruebas de Verificación password_changed_at en Reset Password")
    print("=" * 70)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print()
    
    print("📋 Estos tests verifican que:")
    print("  1. Los tokens con fechas correctas funcionan")
    print("  2. Los tokens con fechas incorrectas son rechazados")
    print("  3. Los tokens sin fecha se manejan apropiadamente")
    print()
    
    try:
        await test_reset_with_valid_token()
        await test_reset_with_invalid_token()
        await test_reset_with_no_date_token()
        
        print("\n" + "=" * 70)
        print("✅ Todas las pruebas completadas")
        
        print("\n💡 Notas importantes:")
        print("  - Estos tests requieren un servidor ejecutándose")
        print("  - Necesitas un usuario existente en la base de datos")
        print("  - Los resultados dependen del estado actual de la DB")
        print("  - Revisa los logs del servidor para más detalles")
        
    except Exception as e:
        print(f"\n❌ Error general en las pruebas: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
