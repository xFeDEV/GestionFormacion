from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.ambiente import AmbienteCreate, AmbienteUpdate, AmbienteOut
from app.crud import ambiente as crud_ambiente
from core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut
from typing import List

router = APIRouter()

def only_admins(user: UserOut):
    if user.id_rol not in [1, 2]:
        raise HTTPException(status_code=401, detail="No autorizado")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_ambiente(
    ambiente: AmbienteCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    only_admins(current_user)
    try:
        crud_ambiente.create_ambiente(db, ambiente)
        return {"message": "Ambiente creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ambiente_id}")
def update_ambiente(
    ambiente_id: int,
    ambiente: AmbienteUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    only_admins(current_user)
    try:
        success = crud_ambiente.update_ambiente(db, ambiente_id, ambiente)
        if not success:
            raise HTTPException(status_code=404, detail="Ambiente no encontrado o sin cambios")
        return {"message": "Ambiente actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ambiente_id}", response_model=AmbienteOut)
def get_ambiente_by_id(ambiente_id: int, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    ambiente = crud_ambiente.get_ambiente_by_id(db, ambiente_id)
    if not ambiente:
        raise HTTPException(status_code=404, detail="Ambiente no encontrado")
    return ambiente

@router.get("/activos/centro/{cod_centro}", response_model=List[AmbienteOut])
def get_ambientes_activos_by_centro(cod_centro: int, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    ambientes = crud_ambiente.get_ambientes_activos_by_centro(db, cod_centro)
    return ambientes

@router.put("/toggle-estado/{ambiente_id}")
def toggle_estado_ambiente(
    ambiente_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    only_admins(current_user)
    try:
        crud_ambiente.toggle_estado_ambiente(db, ambiente_id)
        return {"message": "Estado del ambiente modificado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))