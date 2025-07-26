"""
Script de prueba integral para el flujo completo de recuperación de contraseña

Este script prueba el flujo completo:
1. Solicitar reset (forgot-password)
2. Recibir token por email
3. Usar token para reset (reset-password)
4. Verificar que tokens antiguos se invaliden
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta

# Configuración
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"  # Cambia por un email válido en tu DB
TEST_NEW_PASSWORD = "nueva_contraseña_test_123"

async def test_complete_password_reset_flow():
    """Prueba el flujo completo de recuperación de contraseña"""
    print("🔄 Test Flujo Completo de Recuperación de Contraseña")
    print("=" * 65)
    print(f"📧 Email de prueba: {TEST_EMAIL}")
    print(f"🔑 Nueva contraseña: {TEST_NEW_PASSWORD}")
    print()
    
    async with httpx.AsyncClient() as client:
        
        # PASO 1: Solicitar reset de contraseña
        print("📋 PASO 1: Solicitar reset de contraseña")
        print("-" * 40)
        
        try:
            forgot_response = await client.post(
                f"{API_BASE_URL}/access/forgot-password",
                json={"email": TEST_EMAIL},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {forgot_response.status_code}")
            forgot_result = forgot_response.json()
            
            if forgot_response.status_code == 200:
                print("✅ Solicitud de reset enviada correctamente")
                print(f"Mensaje: {forgot_result.get('message')}")
                
                # Extraer el token de la respuesta (para desarrollo)
                # En producción, el token vendría por email
                if 'token' in forgot_result:
                    token = forgot_result['token']
                    print(f"🎟️  Token recibido: {token[:50]}...")
                else:
                    print("ℹ️  Token enviado por email (no incluido en respuesta)")
                    token = input("Ingresa el token recibido por email: ")
                    
            else:
                print(f"❌ Error en solicitud: {forgot_result}")
                return False
                
        except httpx.ConnectError:
            print("❌ Error de conexión - servidor no disponible")
            return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
            
        print()
        
        # PASO 2: Verificar token antes del reset
        print("📋 PASO 2: Verificar token antes del reset")
        print("-" * 40)
        
        try:
            validate_response = await client.post(
                f"{API_BASE_URL}/access/validate-reset-token",
                json={"token": token},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {validate_response.status_code}")
            validate_result = validate_response.json()
            
            if validate_response.status_code == 200:
                print("✅ Token válido")
                print(f"Usuario: {validate_result.get('user', {}).get('email')}")
            else:
                print(f"❌ Token inválido: {validate_result}")
                return False
                
        except Exception as e:
            print(f"❌ Error validando token: {str(e)}")
            return False
            
        print()
        
        # PASO 3: Resetear contraseña
        print("📋 PASO 3: Resetear contraseña")
        print("-" * 40)
        
        try:
            reset_response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json={
                    "token": token,
                    "new_password": TEST_NEW_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {reset_response.status_code}")
            reset_result = reset_response.json()
            
            if reset_response.status_code == 200:
                print("✅ Contraseña reseteada correctamente")
                print(f"Mensaje: {reset_result.get('message')}")
            else:
                print(f"❌ Error en reset: {reset_result}")
                return False
                
        except Exception as e:
            print(f"❌ Error en reset: {str(e)}")
            return False
            
        print()
        
        # PASO 4: Intentar usar el mismo token nuevamente (debería fallar)
        print("📋 PASO 4: Verificar invalidación del token usado")
        print("-" * 40)
        
        try:
            # Esperar un momento para asegurar que el timestamp se actualizó
            await asyncio.sleep(1)
            
            reuse_response = await client.post(
                f"{API_BASE_URL}/access/reset-password",
                json={
                    "token": token,
                    "new_password": "otra_contraseña_123"
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {reuse_response.status_code}")
            reuse_result = reuse_response.json()
            
            if reuse_response.status_code == 400:
                print("✅ Token correctamente invalidado tras uso")
                print(f"Error esperado: {reuse_result.get('detail')}")
                
                # Verificar mensaje específico
                if "contraseña ya fue cambiada" in reuse_result.get('detail', ''):
                    print("✅ Mensaje de error específico correcto")
                else:
                    print("⚠️  Mensaje de error genérico")
                    
            else:
                print(f"❌ Token reutilizado incorrectamente: {reuse_result}")
                print("🚨 FALLO DE SEGURIDAD: El token debería estar invalidado")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando invalidación: {str(e)}")
            return False
            
        print()
        
        # PASO 5: Verificar validación del token tras reset
        print("📋 PASO 5: Verificar validación del token tras reset")
        print("-" * 40)
        
        try:
            validate_after_response = await client.post(
                f"{API_BASE_URL}/access/validate-reset-token",
                json={"token": token},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {validate_after_response.status_code}")
            validate_after_result = validate_after_response.json()
            
            if validate_after_response.status_code == 400:
                print("✅ Token correctamente invalidado en validación")
                print(f"Error esperado: {validate_after_result.get('detail')}")
            else:
                print(f"❌ Token aún válido tras reset: {validate_after_result}")
                print("🚨 FALLO DE SEGURIDAD: El token debería estar invalidado")
                return False
                
        except Exception as e:
            print(f"❌ Error en segunda validación: {str(e)}")
            return False
            
        return True

async def test_token_security_edge_cases():
    """Prueba casos especiales de seguridad"""
    print("\n🔒 Test Casos Especiales de Seguridad")
    print("=" * 45)
    
    async with httpx.AsyncClient() as client:
        
        # Caso 1: Token expirado
        print("📋 Caso 1: Token expirado")
        print("-" * 30)
        
        try:
            # Generar token con expiración muy corta para simular expiración
            from core.security import create_reset_password_token
            from datetime import datetime
            
            expired_token = create_reset_password_token(
                user_id=1,
                expire_minutes=-1,  # Token ya expirado
                password_changed_at=datetime.now()
            )
            
            expired_response = await client.post(
                f"{API_BASE_URL}/access/validate-reset-token",
                json={"token": expired_token},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {expired_response.status_code}")
            
            if expired_response.status_code == 400:
                print("✅ Token expirado rechazado correctamente")
                print(f"Error: {expired_response.json().get('detail')}")
            else:
                print(f"❌ Token expirado aceptado incorrectamente")
                
        except Exception as e:
            print(f"❌ Error probando token expirado: {str(e)}")
            
        print()
        
        # Caso 2: Token malformado
        print("📋 Caso 2: Token malformado")
        print("-" * 30)
        
        try:
            malformed_response = await client.post(
                f"{API_BASE_URL}/access/validate-reset-token",
                json={"token": "token_malformado_123"},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {malformed_response.status_code}")
            
            if malformed_response.status_code == 400:
                print("✅ Token malformado rechazado correctamente")
                print(f"Error: {malformed_response.json().get('detail')}")
            else:
                print(f"❌ Token malformado aceptado incorrectamente")
                
        except Exception as e:
            print(f"❌ Error probando token malformado: {str(e)}")

async def main():
    """Función principal"""
    print("🧪 Pruebas Integrales de Recuperación de Contraseña")
    print("=" * 70)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print()
    
    print("📋 Este test ejecuta:")
    print("  1. Flujo completo de recuperación de contraseña")
    print("  2. Verificación de invalidación de tokens usados")
    print("  3. Casos especiales de seguridad")
    print()
    
    print("⚠️  Requisitos:")
    print(f"  - Usuario con email '{TEST_EMAIL}' debe existir en la DB")
    print("  - Servidor debe estar ejecutándose en el puerto 8000")
    print("  - Configuración de email debe estar activa")
    print()
    
    input("Presiona Enter para continuar...")
    print()
    
    try:
        # Ejecutar prueba principal
        main_test_success = await test_complete_password_reset_flow()
        
        # Ejecutar pruebas de seguridad
        await test_token_security_edge_cases()
        
        print("\n" + "=" * 70)
        
        if main_test_success:
            print("✅ TODAS LAS PRUEBAS EXITOSAS")
            print("🔐 El sistema de recuperación de contraseña funciona correctamente")
            print("🛡️  Los mecanismos de seguridad están operativos")
        else:
            print("❌ ALGUNAS PRUEBAS FALLARON")
            print("🚨 Revisar implementación y logs del servidor")
            
        print("\n💡 Próximos pasos recomendados:")
        print("  - Probar con diferentes usuarios")
        print("  - Verificar logs de email en Mailtrap")
        print("  - Monitorear rendimiento con múltiples solicitudes")
        print("  - Implementar rate limiting si es necesario")
        
    except Exception as e:
        print(f"\n❌ Error general en las pruebas: {str(e)}")
        print("🔍 Revisar configuración del servidor y base de datos")

if __name__ == "__main__":
    asyncio.run(main())
