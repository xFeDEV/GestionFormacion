from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from app.schemas import notificacion as schemas
from app.schemas.users import UserOut
from app.crud import notificacion as crud_notificacion
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Notificacion])
def get_notificaciones(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todas las notificaciones del usuario actual.
    
    Returns:
        Lista de notificaciones del usuario ordenadas por fecha descendente
    """
    notificaciones = crud_notificacion.get_notifications_by_user_id(
        db=db, 
        user_id=current_user.id_usuario
    )
    
    if notificaciones is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las notificaciones"
        )
    
    return notificaciones

@router.put("/{id_notificacion}/leer")
def marcar_notificacion_leida(
    id_notificacion: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Marca una notificación como leída.
    
    Args:
        id_notificacion: ID de la notificación a marcar como leída
    
    Returns:
        Mensaje de confirmación
    
    Raises:
        HTTPException 404: Si la notificación no existe o no pertenece al usuario
    """
    success = crud_notificacion.mark_notification_as_read(
        db=db,
        notificacion_id=id_notificacion,
        user_id=current_user.id_usuario
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada o no tienes permiso para modificarla"
        )
    
    return {"message": "Notificación marcada como leída exitosamente"}
