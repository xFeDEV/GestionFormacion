from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.grupo_instructor import GrupoInstructorCreate, GrupoInstructorOut
from app.crud import grupo_instructor as crud_grupo_instructor
from core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut
from typing import List

router = APIRouter()

def only_admins(user: UserOut):
    if user.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GrupoInstructorOut)
def assign_instructor_to_grupo(
    grupo_instructor: GrupoInstructorCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    only_admins(current_user)
    try:
        crud_grupo_instructor.create_grupo_instructor(db, grupo_instructor)
        return grupo_instructor
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grupo/{cod_ficha}", response_model=List[GrupoInstructorOut])
def get_instructores_of_grupo(
    cod_ficha: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    instructores = crud_grupo_instructor.get_instructores_by_grupo(db, cod_ficha)
    return instructores

@router.get("/instructor/{id_instructor}", response_model=List[GrupoInstructorOut])
def get_grupos_of_instructor(
    id_instructor: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    grupos = crud_grupo_instructor.get_grupos_by_instructor(db, id_instructor)
    return grupos

@router.delete("/{cod_ficha}/{id_instructor}", status_code=status.HTTP_204_NO_CONTENT)
def unassign_instructor_from_grupo(
    cod_ficha: int,
    id_instructor: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    only_admins(current_user)
    try:
        success = crud_grupo_instructor.delete_grupo_instructor(db, cod_ficha, id_instructor)
        if not success:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))