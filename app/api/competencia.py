from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from app.schemas.competencia import CompetenciaCreate, CompetenciaOut, CompetenciaUpdate
from app.crud import competencia as crud_competencia
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut

router = APIRouter()

def only_admins(user: UserOut):
    """Validar que solo admin y superadmin puedan modificar competencias."""
    if user.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.get("/programa/{cod_programa}/{la_version}", response_model=List[CompetenciaOut])
def get_competencias_by_programa(
    cod_programa: int,
    la_version: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todas las competencias relacionadas a un programa de formación específico.
    
    Nota: Las competencias están asociadas al programa en general, no a una versión específica,
    por lo que el parámetro la_version se mantiene por compatibilidad pero no afecta el resultado.
    """
    try:
        competencias = crud_competencia.get_competencias_by_programa(db, cod_programa, la_version)
        return competencias
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_competencia(
    competencia: CompetenciaCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Crear una nueva competencia.
    """
    only_admins(current_user)
    try:
        # Verificar si ya existe
        existing = crud_competencia.get_competencia_by_id(db, competencia.cod_competencia)
        if existing:
            raise HTTPException(status_code=400, detail="La competencia ya existe")
        
        crud_competencia.create_competencia(db, competencia)
        return {"message": "Competencia creada correctamente"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cod_competencia}", response_model=CompetenciaOut)
def get_competencia(
    cod_competencia: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtener una competencia específica por su código.
    """
    try:
        competencia = crud_competencia.get_competencia_by_id(db, cod_competencia)
        if not competencia:
            raise HTTPException(status_code=404, detail="Competencia no encontrada")
        return competencia
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CompetenciaOut])
def get_all_competencias(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtener todas las competencias.
    """
    try:
        competencias = crud_competencia.get_all_competencias(db)
        return competencias
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{cod_competencia}")
def update_competencia(
    cod_competencia: int,
    competencia_update: CompetenciaUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Actualizar una competencia existente.
    """
    only_admins(current_user)
    try:
        # Verificar si existe
        existing = crud_competencia.get_competencia_by_id(db, cod_competencia)
        if not existing:
            raise HTTPException(status_code=404, detail="Competencia no encontrada")
        
        success = crud_competencia.update_competencia(db, cod_competencia, competencia_update)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la competencia")
        
        return {"message": "Competencia actualizada correctamente"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{cod_competencia}", status_code=status.HTTP_204_NO_CONTENT)
def delete_competencia(
    cod_competencia: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Eliminar una competencia.
    """
    only_admins(current_user)
    try:
        # Verificar si existe
        existing = crud_competencia.get_competencia_by_id(db, cod_competencia)
        if not existing:
            raise HTTPException(status_code=404, detail="Competencia no encontrada")
        
        success = crud_competencia.delete_competencia(db, cod_competencia)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo eliminar la competencia")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cod_competencia}/programas")
def get_programas_by_competencia(
    cod_competencia: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todos los programas de formación que incluyen una competencia específica.
    """
    try:
        # Verificar si la competencia existe
        competencia = crud_competencia.get_competencia_by_id(db, cod_competencia)
        if not competencia:
            raise HTTPException(status_code=404, detail="Competencia no encontrada")
        
        programas = crud_competencia.get_programas_by_competencia(db, cod_competencia)
        return programas
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) 