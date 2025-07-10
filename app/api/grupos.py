from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.grupos import GrupoUpdate, GrupoOut
from app.crud import grupos as crud_grupo
from core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut

router = APIRouter()

@router.get("/{cod_ficha}", response_model=GrupoOut)
def get_grupo(
    cod_ficha: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene un grupo específico por su cod_ficha.
    Maneja correctamente los valores nulos y los horarios en 00:00:00.
    """
    try:
        grupo = crud_grupo.get_grupo_by_cod_ficha(db, cod_ficha=cod_ficha)
        if grupo is None:
            raise HTTPException(status_code=404, detail="Grupo no encontrado")
        return grupo
    except Exception as e:
        # Evita reenviar el detalle de una excepción HTTP ya lanzada
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{cod_ficha}")
def update_grupo(
    cod_ficha: int,
    grupo: GrupoUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Actualiza la hora de inicio, hora de fin y el aula actual de un grupo específico.
    """
    # Solo superadmin (1) y admin (2) pueden actualizar
    if current_user.id_rol not in [1, 2]:
        raise HTTPException(status_code=401, detail="No autorizado para realizar esta acción")

    try:
        success = crud_grupo.update_grupo(db, cod_ficha, grupo)
        if not success:
            raise HTTPException(status_code=404, detail="Grupo no encontrado o sin cambios para aplicar")
        return {"message": "Grupo actualizado correctamente"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
