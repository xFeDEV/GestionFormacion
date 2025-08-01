from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.programas import ProgramaCreate, ProgramaUpdate, ProgramaOut, ProgramaPage
from app.crud import programas as crud_programa
from core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut
from typing import List

router = APIRouter(prefix="/programas")

def only_admins(user: UserOut):
    if user.id_rol not in [1, 2]:
        raise HTTPException(status_code=401, detail="No autorizado")

@router.post("/", status_code=status.HTTP_201_CREATED)

def create_programa(
    programa: ProgramaCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    only_admins(current_user)
    try:
        crud_programa.create_programa(db, programa)
        return {"message": "Programa creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=ProgramaPage)
def get_all_programas(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db), 
    current_user: UserOut = Depends(get_current_user)
):
    result = crud_programa.get_programas(db, skip=skip, limit=limit)
    return result

@router.get("/search/", response_model=ProgramaPage)
def search_programas(
    query: str,
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db), 
    current_user: UserOut = Depends(get_current_user)
):
    try:
        result = crud_programa.search_programas(db, search_term=query, skip=skip, limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cod_programa}", response_model=ProgramaOut)
def get_programa_by_id(cod_programa: int, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    programa = crud_programa.get_programa(db, cod_programa=cod_programa)
    if not programa:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    return programa

@router.put("/{cod_programa}")
def update_programa(
    cod_programa: int,
    programa: ProgramaUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    only_admins(current_user)
    try:
        success = crud_programa.update_programa(db, cod_programa, programa)
        if not success:
            raise HTTPException(status_code=404, detail="Programa no encontrado o sin cambios")
        return {"message": "Programa actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
