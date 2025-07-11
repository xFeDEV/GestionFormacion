from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.ambiente import AmbienteCreate, AmbienteUpdate
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def create_ambiente(db: Session, ambiente: AmbienteCreate) -> bool:
    try:
        query = text("""
            INSERT INTO ambiente_formacion (
                nombre_ambiente, num_max_aprendices, municipio, ubicacion, cod_centro, estado
            ) VALUES (
                :nombre_ambiente, :num_max_aprendices, :municipio, :ubicacion, :cod_centro, :estado
            )
        """)
        db.execute(query, ambiente.model_dump())
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear ambiente: {e}")
        raise Exception("Error de base de datos al crear el ambiente")

def update_ambiente(db: Session, ambiente_id: int, ambiente: AmbienteUpdate) -> bool:
    try:
        fields = ambiente.model_dump(exclude_unset=True)
        if not fields:
            return False
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])
        fields["ambiente_id"] = ambiente_id
        query = text(f"UPDATE ambiente_formacion SET {set_clause} WHERE id_ambiente = :ambiente_id")
        db.execute(query, fields)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar ambiente: {e}")
        raise Exception("Error de base de datos al actualizar el ambiente")

def get_ambiente_by_id(db: Session, ambiente_id: int):
    try:
        query = text("SELECT * FROM ambiente_formacion WHERE id_ambiente = :ambiente_id")
        result = db.execute(query, {"ambiente_id": ambiente_id}).mappings().first()
        return result
    except Exception as e:
        logger.error(f"Error al obtener ambiente: {e}")
        raise Exception("Error de base de datos al obtener el ambiente")

def get_ambientes_activos_by_centro(db: Session, cod_centro: int):
    try:
        query = text("""
            SELECT * FROM ambiente_formacion
            WHERE cod_centro = :cod_centro
        """)
        result = db.execute(query, {"cod_centro": cod_centro}).mappings().all()
        return result
    except Exception as e:
        logger.error(f"Error al obtener ambientes activos: {e}")
        raise Exception("Error de base de datos al obtener los ambientes activos")

def toggle_estado_ambiente(db: Session, ambiente_id: int) -> bool:
    try:
        query = text("""
            UPDATE ambiente_formacion
            SET estado = NOT estado
            WHERE id_ambiente = :ambiente_id
        """)
        db.execute(query, {"ambiente_id": ambiente_id})
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error al modificar estado del ambiente: {e}")
        raise Exception("Error de base de datos al modificar el estado del ambiente")