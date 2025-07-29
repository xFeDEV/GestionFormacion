from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
import logging
from app.schemas import notificacion as schemas

logger = logging.getLogger(__name__)

def create_notification(db: Session, notificacion: schemas.NotificacionCreate) -> Optional[bool]:
    """
    Crea una nueva notificación en la base de datos.
    
    Args:
        db: Sesión de base de datos
        notificacion: Objeto con los datos de la notificación a crear
    
    Returns:
        True si fue exitoso, None si hubo error
    """
    try:
        notificacion_data = notificacion.model_dump()
        query = text("""
            INSERT INTO notificacion (
                id_usuario, mensaje, leida
            ) VALUES (
                :id_usuario, :mensaje, :leida
            )
        """)
        db.execute(query, notificacion_data)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear notificación: {e}")
        return None

def get_notifications_by_user_id(db: Session, user_id: int) -> Optional[List]:
    """
    Obtiene todas las notificaciones de un usuario específico ordenadas por fecha descendente.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
    
    Returns:
        Lista de notificaciones o None si hubo error
    """
    try:
        query = text("""
            SELECT 
                id_notificacion,
                id_usuario,
                mensaje,
                leida,
                fecha_creacion
            FROM notificacion
            WHERE id_usuario = :user_id
            ORDER BY fecha_creacion DESC
        """)
        result = db.execute(query, {"user_id": user_id}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener notificaciones del usuario {user_id}: {e}")
        return None

def mark_notification_as_read(db: Session, notificacion_id: int, user_id: int) -> bool:
    """
    Marca una notificación como leída, verificando que pertenezca al usuario.
    
    Args:
        db: Sesión de base de datos
        notificacion_id: ID de la notificación
        user_id: ID del usuario (para verificar pertenencia)
    
    Returns:
        True si fue exitoso, False si no
    """
    try:
        # Primero verificamos que la notificación existe y pertenece al usuario
        verify_query = text("""
            SELECT id_notificacion 
            FROM notificacion 
            WHERE id_notificacion = :notificacion_id AND id_usuario = :user_id
        """)
        result = db.execute(verify_query, {
            "notificacion_id": notificacion_id,
            "user_id": user_id
        }).mappings().first()
        
        if not result:
            logger.warning(f"Notificación {notificacion_id} no encontrada o no pertenece al usuario {user_id}")
            return False
        
        # Si existe y pertenece al usuario, la marcamos como leída
        update_query = text("""
            UPDATE notificacion 
            SET leida = TRUE 
            WHERE id_notificacion = :notificacion_id AND id_usuario = :user_id
        """)
        db.execute(update_query, {
            "notificacion_id": notificacion_id,
            "user_id": user_id
        })
        db.commit()
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al marcar notificación como leída: {e}")
        return False
