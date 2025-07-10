from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.grupos import GrupoUpdate
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_grupo_by_cod_ficha(db: Session, cod_ficha: int) -> Optional[dict]:
    """
    Obtiene un grupo específico por su cod_ficha.
    """
    try:
        query = text("SELECT * FROM grupo WHERE cod_ficha = :cod_ficha")
        result = db.execute(query, {"cod_ficha": cod_ficha}).mappings().first()
        return result
    except Exception as e:
        logger.error(f"Error al obtener el grupo {cod_ficha}: {e}")
        raise Exception("Error de base de datos al obtener el grupo")

def update_grupo(db: Session, cod_ficha: int, grupo: GrupoUpdate) -> bool:
    try:
        # Obtiene solo los campos que el usuario envió en la petición
        fields = grupo.model_dump(exclude_unset=True)

        # Si no se envió ningún dato para actualizar, no hace nada
        if not fields:
            return False
        
        # Construye la parte SET de la consulta SQL dinámicamente
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])

        # Agrega el cod_ficha para el WHERE
        params = {"cod_ficha": cod_ficha, **fields}
        
        query = text(f"UPDATE grupo SET {set_clause} WHERE cod_ficha = :cod_ficha")
        
        result = db.execute(query, params)
        db.commit()
        
        return result.rowcount > 0
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar el grupo: {e}")
        raise Exception("Error de base de datos al actualizar el grupo")
