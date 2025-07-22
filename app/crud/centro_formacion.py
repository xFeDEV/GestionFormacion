from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.centro_formacion import CentroFormacionOut
import logging


logger = logging.getLogger(__name__)

def get_all_centros_formacion(db: Session) -> List[CentroFormacionOut]:
    """
    Obtiene todos los centros de formación.
    """
    try:
        query = text("SELECT * FROM centro_formacion")
        results = db.execute(query).mappings().all()
        return [CentroFormacionOut.model_validate(result) for result in results]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener centros de formación: {e}")
        raise


def get_centro_formacion_by_cod_centro(db: Session, cod_centro: int) -> Optional[CentroFormacionOut]:
    """
    Obtiene un centro de formación específico por su cod_centro.
    """
    try:
        query = text("SELECT * FROM centro_formacion WHERE cod_centro = :cod_centro")
        result = db.execute(query, {"cod_centro": cod_centro}).mappings().first()
        return CentroFormacionOut.model_validate(result)
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el centro de formación {cod_centro}: {e}")
        raise


def get_centro_formacion_by_nombre(db: Session, nombre_centro: str) -> Optional[CentroFormacionOut]:
    """
    Obtiene un centro de formación específico por nombre del centro.
    """
    try:
        query = text("SELECT * FROM centro_formacion WHERE nombre_centro = :nombre_centro")
        result = db.execute(query, {"nombre_centro": nombre_centro}).mappings().first()
        return CentroFormacionOut.model_validate(result)
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el centro de formación por el nombre del centro {nombre_centro}: {e}")
        raise


def get_centro_formacion_by_cod_regional(db: Session, cod_regional: int) -> List[CentroFormacionOut]:
    """
    Obtiene un centro de formación específico por el codigo de regional.
    """
    try:
        query = text("SELECT * FROM centro_formacion WHERE cod_regional = :cod_regional")
        results = db.execute(query, {"cod_regional": cod_regional}).mappings().all()
        return [CentroFormacionOut.model_validate(result) for result in results]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el centro de formación con el codigo de regional {cod_regional}: {e}")
        raise
