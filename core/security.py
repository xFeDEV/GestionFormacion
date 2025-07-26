from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from core.config import settings
from fastapi import Depends
from sqlalchemy.orm import Session
from app.crud import users as crud_users
from core.database import get_db

# Configurar hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para generar un hashed_password
def get_hashed_password(password: str):
    return pwd_context.hash(password)

# Función para verificar una contraseña hashada
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Función para crear un token JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

# Función para crear un token de recuperación de contraseña con duración personalizada
def create_reset_password_token(user_id: int, expire_minutes: int = 15, password_changed_at=None):
    """
    Crear un token JWT específico para recuperación de contraseña
    
    Args:
        user_id: ID del usuario
        expire_minutes: Minutos de expiración (default: 15)
        password_changed_at: Fecha del último cambio de contraseña (opcional)
    
    Returns:
        str: Token JWT codificado
    """
    to_encode = {
        "sub": str(user_id),
        "type": "password_reset"
    }
    
    # Añadir password_changed_at al payload si está disponible
    if password_changed_at is not None:
        # Convertir datetime a string para que sea compatible con JSON
        if hasattr(password_changed_at, 'isoformat'):
            to_encode["password_changed_at"] = password_changed_at.isoformat()
        else:
            to_encode["password_changed_at"] = str(password_changed_at)
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

# Función para verificar si un token JWT es valido
def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        return int(user_id) if user_id is not None else None
    except jwt.ExpiredSignatureError: # Token ha expirado
        print("Token expirado")
        return None
    except JWTError as e:
        print("Error al decodificar el token:", str(e))
        return None

# Función para verificar token de recuperación de contraseña
def verify_reset_password_token(token: str, db: Session = Depends(get_db)):
    """
    Verifica un token de reseteo. Revisa firma, expiración y si ya fue usado
    comparando el timestamp 'password_changed_at'.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        
        token_type = payload.get("type")
        if token_type != "password_reset":
            return None # No es un token de reseteo

        user_id = payload.get("sub")
        token_timestamp_str = payload.get("password_changed_at")

        if not user_id:
            return None

        # --- La Lógica de Verificación Completa ---
        user_in_db = crud_users.get_user_by_id(db, int(user_id))
        if not user_in_db:
            return None # El usuario del token ya no existe

        db_timestamp_str = user_in_db.password_changed_at.isoformat() if user_in_db.password_changed_at else None

        # Si los timestamps no coinciden, el token es viejo y ya fue usado
        if token_timestamp_str != db_timestamp_str:
            return None

        # Si todo está bien, devuelve el payload
        return payload

    except JWTError:
        return None