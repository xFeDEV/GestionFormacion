from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.users import UserOut
from app.schemas.centro_formacion import CentroFormacionOut
from app.crud import centro_formacion as CrudCentroFormacion
from app.api.dependencies import get_current_user
from core.database import get_db

router = APIRouter()

"""
Solo se obtiene informacion de los centros de formación, no se permite crear, actualizar o eliminar centros de formación.
"""

@router.get("/centros", response_model=List[CentroFormacionOut])
def get_all_centros_formacion(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todos los centros de formación.
    """
    centros_formacion = CrudCentroFormacion.get_all_centros_formacion(db)
    return centros_formacion


@router.get("/{cod_centro}", response_model=CentroFormacionOut)
def get_centro_formacion(
    cod_centro: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):  
    """
    Obtiene un centro de formación específico por su cod_centro.
    """
    centro_formacion = CrudCentroFormacion.get_centro_formacion_by_cod_centro(db, cod_centro=cod_centro)
    if centro_formacion is None:
        raise HTTPException(status_code=404, detail="Centro de formación no encontrado")
    return centro_formacion


@router.get("/nombre/{nombre_centro}", response_model=CentroFormacionOut)
def get_centro_formacion_by_nombre(
    nombre: str,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene un centro de formación específico por nombre del centro.
    """
    centro_formacion = CrudCentroFormacion.get_centro_formacion_by_nombre(db, nombre_centro=nombre)
    if centro_formacion is None:
        raise HTTPException(status_code=404, detail="Centro de formación no encontrado")
    return centro_formacion


@router.get("/regional/{cod_regional}", response_model= List[CentroFormacionOut])
def get_centro_formacion_by_cod_regional(
    cod_regional: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene un centro de formación específico por el codigo de regional.
    """
    centros_formacion = CrudCentroFormacion.get_centro_formacion_by_cod_regional(db, cod_regional=cod_regional)
    if not centros_formacion:
        raise HTTPException(status_code=404, detail="Centros de formación no encontrados para la región especificada")
    return centros_formacion