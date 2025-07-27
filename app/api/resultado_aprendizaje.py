from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.resultado_aprendizaje import ResultadoAprendizajeOut
from app.crud import programacion as crud_programacion
from core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut
from typing import List

router = APIRouter()

@router.get("/competencia/{cod_competencia}", response_model=List[ResultadoAprendizajeOut])
def get_resultados_by_competencia(
    cod_competencia: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todos los resultados de aprendizaje para una competencia específica.
    
    Parámetros:
    - cod_competencia: Código de la competencia para la cual obtener los resultados
    
    Respuesta:
    - Array de objetos con cod_resultado, nombre, cod_competencia y horas
    """
    try:
        resultados = crud_programacion.get_resultados_by_competencia(db, cod_competencia=cod_competencia)
        return resultados
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) 