from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.competencia import CompetenciaCreate, CompetenciaUpdate
from typing import List
import logging

logger = logging.getLogger(__name__)

def get_competencias_by_programa(db: Session, cod_programa: int, la_version: int = None):
    """
    Obtiene todas las competencias asociadas a un programa de formación específico.
    Nota: Las competencias están asociadas al programa, no a una versión específica.
    """
    try:
        query = text("""
            SELECT DISTINCT c.cod_competencia, c.nombre, c.horas
            FROM competencia c
            INNER JOIN programa_competencia pc ON c.cod_competencia = pc.cod_competencia
            WHERE pc.cod_programa = :cod_programa
            ORDER BY c.cod_competencia
        """)
        result = db.execute(query, {
            "cod_programa": cod_programa
        }).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener competencias por programa: {e}")
        raise Exception("Error de base de datos al obtener competencias del programa")

def create_competencia(db: Session, competencia: CompetenciaCreate):
    """
    Crear una nueva competencia.
    """
    try:
        query = text("""
            INSERT INTO competencia (cod_competencia, nombre, horas)
            VALUES (:cod_competencia, :nombre, :horas)
        """)
        db.execute(query, competencia.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear competencia: {e}")
        raise Exception("Error de base de datos al crear la competencia")

def get_competencia_by_id(db: Session, cod_competencia: int):
    """
    Obtener una competencia por su código.
    """
    try:
        query = text("""
            SELECT cod_competencia, nombre, horas
            FROM competencia
            WHERE cod_competencia = :cod_competencia
        """)
        result = db.execute(query, {"cod_competencia": cod_competencia}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener competencia por ID: {e}")
        raise Exception("Error de base de datos al obtener la competencia")

def get_all_competencias(db: Session):
    """
    Obtener todas las competencias.
    """
    try:
        query = text("""
            SELECT cod_competencia, nombre, horas
            FROM competencia
            ORDER BY cod_competencia
        """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener todas las competencias: {e}")
        raise Exception("Error de base de datos al obtener las competencias")

def update_competencia(db: Session, cod_competencia: int, competencia_update: CompetenciaUpdate) -> bool:
    """
    Actualizar una competencia existente.
    """
    try:
        # Construir query dinámicamente según los campos a actualizar
        fields = competencia_update.model_dump(exclude_unset=True)
        if not fields:
            return False
        
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])
        fields["cod_competencia"] = cod_competencia
        
        query = text(f"""
            UPDATE competencia 
            SET {set_clause}
            WHERE cod_competencia = :cod_competencia
        """)
        
        result = db.execute(query, fields)
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar competencia: {e}")
        raise Exception("Error de base de datos al actualizar la competencia")

def delete_competencia(db: Session, cod_competencia: int) -> bool:
    """
    Eliminar una competencia.
    """
    try:
        query = text("""
            DELETE FROM competencia
            WHERE cod_competencia = :cod_competencia
        """)
        result = db.execute(query, {"cod_competencia": cod_competencia})
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar competencia: {e}")
        raise Exception("Error de base de datos al eliminar la competencia")

def get_programas_by_competencia(db: Session, cod_competencia: int):
    """
    Obtener todos los programas que incluyen una competencia específica.
    Nota: Retorna todas las versiones de los programas que incluyen esta competencia.
    """
    try:
        query = text("""
            SELECT DISTINCT pf.cod_programa, pf.la_version, pf.nombre as nombre_programa
            FROM programa_formacion pf
            INNER JOIN programa_competencia pc ON pf.cod_programa = pc.cod_programa
            WHERE pc.cod_competencia = :cod_competencia
            ORDER BY pf.cod_programa, pf.la_version
        """)
        result = db.execute(query, {"cod_competencia": cod_competencia}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener programas por competencia: {e}")
        raise Exception("Error de base de datos al obtener programas de la competencia") 