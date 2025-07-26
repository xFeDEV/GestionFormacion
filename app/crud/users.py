from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import logging
from app.schemas.users import UserCreate, UserUpdate
from core.security import get_hashed_password, verify_password, verify_reset_password_token

logger = logging.getLogger(__name__)

def create_user(db: Session, user: UserCreate) -> Optional[bool]:
    try:
        pass_hashed = get_hashed_password(user.pass_hash)
        user_data = user.model_dump()
        user_data['pass_hash'] = pass_hashed
        query = text("""
            INSERT INTO usuario (
                nombre_completo, identificacion, id_rol,
                correo, pass_hash, tipo_contrato,
                telefono, estado, cod_centro
            ) VALUES (
                :nombre_completo, :identificacion, :id_rol,
                :correo, :pass_hash, :tipo_contrato,
                :telefono, :estado, :cod_centro
            )
        """)
        db.execute(query, user_data)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {e}")
        raise Exception("Error de base de datos al crear el usuario")

def get_user_by_email(db: Session, email: str):
    try:
        query = text("""
            SELECT u.id_usuario, u.nombre_completo, u.identificacion, u.id_rol, r.nombre AS nombre_rol,
                   u.correo, u.tipo_contrato, u.pass_hash, u.telefono, u.estado, u.cod_centro, u.password_changed_at
            FROM usuario u
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.correo = :direccion_correo
        """)
        result = db.execute(query, {"direccion_correo": email}).mappings().first()
        if not result:
            return None
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por email: {e}")
        raise Exception("Error de base de datos al obtener el usuario")


def get_user_by_id(db: Session, id_user: int):
    try:
        query = text("""
            SELECT u.id_usuario, u.nombre_completo, u.identificacion, u.id_rol, r.nombre AS nombre_rol,
                   u.correo, u.tipo_contrato, u.telefono, u.estado, u.cod_centro, u.password_changed_at
            FROM usuario u
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.id_usuario = :id
        """)
        result = db.execute(query, {"id": id_user}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por id: {e}")
        raise Exception("Error de base de datos al obtener el usuario")


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> bool:
    try:
        fields = user_update.model_dump(exclude_unset=True)
        if not fields:
            return False
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])
        fields["user_id"] = user_id

        query = text(f"UPDATE usuario SET {set_clause} WHERE id_usuario = :user_id")
        db.execute(query, fields)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario: {e}")
        raise Exception("Error de base de datos al actualizar el usuario")


def modify_status_user(db: Session, user_id: int):
    try:
        query = text( """
                     UPDATE usuario SET estado = IF(estado, FALSE, TRUE)
                     WHERE id_usuario = :id
                    """ )
        db.execute(query, {"id": user_id})
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al modificar el estado de usuario: {e}")
        raise Exception("Error de base de datos al modificar estado del usuario")
    
def get_users_by_centro(db: Session, cod_centro: int):
    try:
        query = text("""
            SELECT u.id_usuario, u.nombre_completo, u.identificacion, u.id_rol, r.nombre AS nombre_rol,
                   u.correo, u.tipo_contrato, u.telefono, u.estado, u.cod_centro
            FROM usuario u
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.cod_centro = :cod_centro
        """)
        result = db.execute(query, {"cod_centro": cod_centro}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuarios por cod_centro: {e}")
        raise Exception("Error de base de datos al obtener los usuarios")

def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
    try:
        # Obtener el usuario por su ID junto con su contraseña hasheada
        query = text("""
            SELECT id_usuario, pass_hash
            FROM usuario
            WHERE id_usuario = :user_id
        """)
        result = db.execute(query, {"user_id": user_id}).mappings().first()
        
        if not result:
            return False
        
        # Verificar que la contraseña actual sea correcta
        if not verify_password(current_password, result.pass_hash):
            return False
        
        # Hashear la nueva contraseña
        new_hashed_password = get_hashed_password(new_password)
        
        # Actualizar la contraseña y la fecha de cambio en la base de datos
        update_query = text("""
            UPDATE usuario 
            SET pass_hash = :new_password, password_changed_at = NOW()
            WHERE id_usuario = :user_id
        """)
        db.execute(update_query, {
            "new_password": new_hashed_password,
            "user_id": user_id
        })
        db.commit()
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar contraseña: {e}")
        raise Exception("Error de base de datos al cambiar la contraseña")


def reset_password(db: Session, token: str, new_password: str) -> Optional[bool]:
    """
    Restablecer contraseña usando un token de recuperación
    
    Args:
        db: Sesión de base de datos
        token: Token JWT de recuperación de contraseña
        new_password: Nueva contraseña en texto plano
    
    Returns:
        True si fue exitoso, None si el token es inválido
    """
    try:
        # Decodificar el token para obtener el user_id
        token_data = verify_reset_password_token(token, db)
        
        if not token_data:
            logger.warning("Intento de reset con token inválido o expirado")
            return None
            
        user_id = token_data.get("sub")
        if not user_id:
            logger.warning("Token de reset no contiene user_id válido")
            return None
        
        # Verificar que el usuario existe
        user_query = text("""
            SELECT id_usuario 
            FROM usuario 
            WHERE id_usuario = :user_id
        """)
        user_result = db.execute(user_query, {"user_id": user_id}).mappings().first()
        
        if not user_result:
            logger.warning(f"Usuario con ID {user_id} no encontrado para reset de contraseña")
            return None
        
        # Hashear la nueva contraseña
        new_hashed_password = get_hashed_password(new_password)
        
        # Actualizar la contraseña y la fecha de cambio en la base de datos
        update_query = text("""
            UPDATE usuario 
            SET pass_hash = :new_password, password_changed_at = NOW()
            WHERE id_usuario = :user_id
        """)
        db.execute(update_query, {
            "new_password": new_hashed_password,
            "user_id": user_id
        })
        db.commit()
        
        logger.info(f"Contraseña restablecida exitosamente para usuario ID: {user_id}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al restablecer contraseña: {e}")
        raise Exception("Error de base de datos al restablecer la contraseña")
    except Exception as e:
        logger.error(f"Error inesperado al restablecer contraseña: {e}")
        return None

def get_instructores(db: Session):
    """
    Obtiene todos los usuarios que tienen el rol de instructor (id_rol = 3).
    """
    try:
        query = text("""
            SELECT u.id_usuario, u.nombre_completo, u.identificacion, u.id_rol, r.nombre AS nombre_rol,
                   u.correo, u.tipo_contrato, u.telefono, u.estado, u.cod_centro
            FROM usuario u
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.id_rol = 3 AND u.estado = 1
            ORDER BY u.nombre_completo
        """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener instructores: {e}")
        raise Exception("Error de base de datos al obtener los instructores")
