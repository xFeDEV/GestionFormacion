"""
Script de prueba para verificar el campo password_changed_at en tokens

Este script verifica que el campo password_changed_at se incluye correctamente
en los tokens de recuperación de contraseña.
"""

import json
from datetime import datetime
from core.security import create_reset_password_token, verify_reset_password_token

def test_token_with_password_changed_at():
    """Probar creación de token con password_changed_at"""
    print("🔐 Probando token con password_changed_at")
    print("=" * 50)
    
    # Datos de prueba
    user_id = 123
    test_datetime = datetime.now()
    
    print(f"User ID: {user_id}")
    print(f"Password changed at: {test_datetime}")
    print()
    
    # Crear token con password_changed_at
    print("1. Creando token con password_changed_at...")
    token_with_date = create_reset_password_token(
        user_id=user_id,
        expire_minutes=15,
        password_changed_at=test_datetime
    )
    
    print(f"Token generado: {token_with_date[:50]}...")
    print()
    
    # Verificar token
    print("2. Verificando contenido del token...")
    token_data = verify_reset_password_token(token_with_date)
    
    if token_data:
        print("✅ Token válido")
        print(f"User ID en token: {token_data.get('user_id')}")
        print(f"Tipo de token: {token_data.get('type')}")
        
        # Verificar password_changed_at
        password_changed_at_str = token_data.get('password_changed_at')
        if password_changed_at_str:
            print(f"Password changed at en token: {password_changed_at_str}")
            print("✅ Campo password_changed_at incluido correctamente")
        else:
            print("❌ Campo password_changed_at no encontrado en token")
    else:
        print("❌ Token inválido")
    
    print()
    return token_data

def test_token_without_password_changed_at():
    """Probar creación de token sin password_changed_at"""
    print("🔐 Probando token sin password_changed_at")
    print("=" * 50)
    
    user_id = 456
    
    print(f"User ID: {user_id}")
    print("Password changed at: None")
    print()
    
    # Crear token sin password_changed_at
    print("1. Creando token sin password_changed_at...")
    token_without_date = create_reset_password_token(
        user_id=user_id,
        expire_minutes=15
        # password_changed_at no se proporciona
    )
    
    print(f"Token generado: {token_without_date[:50]}...")
    print()
    
    # Verificar token
    print("2. Verificando contenido del token...")
    token_data = verify_reset_password_token(token_without_date)
    
    if token_data:
        print("✅ Token válido")
        print(f"User ID en token: {token_data.get('user_id')}")
        print(f"Tipo de token: {token_data.get('type')}")
        
        # Verificar que password_changed_at no esté presente
        password_changed_at_str = token_data.get('password_changed_at')
        if password_changed_at_str:
            print(f"Password changed at en token: {password_changed_at_str}")
            print("⚠️  Campo password_changed_at presente inesperadamente")
        else:
            print("✅ Campo password_changed_at no presente (correcto)")
    else:
        print("❌ Token inválido")
    
    print()
    return token_data

def test_different_date_formats():
    """Probar diferentes formatos de fecha"""
    print("📅 Probando diferentes formatos de fecha")
    print("=" * 50)
    
    user_id = 789
    
    # Diferentes tipos de fecha
    test_cases = [
        ("datetime actual", datetime.now()),
        ("string ISO", "2025-01-15T10:30:00"),
        ("None", None),
    ]
    
    for description, date_value in test_cases:
        print(f"Probando con {description}: {date_value}")
        
        try:
            token = create_reset_password_token(
                user_id=user_id,
                expire_minutes=15,
                password_changed_at=date_value
            )
            
            token_data = verify_reset_password_token(token)
            if token_data:
                password_changed_at_in_token = token_data.get('password_changed_at')
                print(f"  ✅ Token creado. password_changed_at: {password_changed_at_in_token}")
            else:
                print("  ❌ Token inválido")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()

def main():
    """Función principal"""
    print("🧪 Pruebas de password_changed_at en Tokens")
    print("=" * 60)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Ejecutar pruebas
        test_token_with_password_changed_at()
        test_token_without_password_changed_at()
        test_different_date_formats()
        
        print("=" * 60)
        print("✅ Todas las pruebas completadas")
        
        print("\n💡 Uso en el endpoint:")
        print("```python")
        print("reset_token = create_reset_password_token(")
        print("    user_id=user.id_usuario,")
        print("    expire_minutes=15,")
        print("    password_changed_at=user.password_changed_at")
        print(")")
        print("```")
        
    except Exception as e:
        print(f"\n❌ Error general en las pruebas: {str(e)}")

if __name__ == "__main__":
    main()
