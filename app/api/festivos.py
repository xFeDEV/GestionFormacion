from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.festivos import FestivoOut, FestivosResponse
from app.crud import festivos as crud_festivos
from core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut
from typing import List, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[FestivoOut])
def get_all_festivos(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todos los días festivos registrados en la base de datos.
    
    Returns:
        List[FestivoOut]: Lista de todos los festivos
    """
    try:
        festivos = crud_festivos.get_festivos(db)
        return [{"festivo": festivo} for festivo in festivos]
    except Exception as e:
        logger.error(f"Error al obtener festivos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/year/{year}", response_model=List[FestivoOut])
def get_festivos_by_year(
    year: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene los días festivos de un año específico.
    
    Args:
        year: Año para filtrar los festivos
        
    Returns:
        List[FestivoOut]: Lista de festivos del año especificado
    """
    try:
        if year < 1900 or year > 2100:
            raise HTTPException(status_code=400, detail="Año debe estar entre 1900 y 2100")
        
        festivos = crud_festivos.get_festivos_by_year(db, year)
        return [{"festivo": festivo} for festivo in festivos]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener festivos por año: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/festivos-y-domingos", response_model=FestivosResponse)
def get_festivos_y_domingos(
    year: Optional[int] = Query(None, description="Año para filtrar (opcional, por defecto año actual)"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene los días festivos y domingos.
    Si no se especifica año, retorna festivos de todos los años y domingos del año actual.
    Si se especifica año, retorna festivos y domingos de ese año.
    
    Args:
        year: Año para filtrar (opcional)
        
    Returns:
        FestivosResponse: Objeto con festivos, domingos y total de días
    """
    try:
        if year and (year < 1900 or year > 2100):
            raise HTTPException(status_code=400, detail="Año debe estar entre 1900 y 2100")
        
        result = crud_festivos.get_festivos_y_domingos(db, year)
        return FestivosResponse(
            festivos=result["festivos"],
            domingos=result["domingos"],
            total_dias=result["total_dias"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener festivos y domingos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/domingos/{year}")
def get_domingos_by_year(
    year: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todos los domingos de un año específico.
    
    Args:
        year: Año para obtener los domingos
        
    Returns:
        Dict con la lista de domingos del año
    """
    try:
        if year < 1900 or year > 2100:
            raise HTTPException(status_code=400, detail="Año debe estar entre 1900 y 2100")
        
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        domingos = crud_festivos.get_domingos_in_range(start_date, end_date)
        
        return {
            "year": year,
            "domingos": domingos,
            "total_domingos": len(domingos)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener domingos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
