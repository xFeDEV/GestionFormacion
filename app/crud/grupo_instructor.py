from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.grupo_instructor import GrupoInstructorCreate, GrupoInstructorUpdate
import logging

logger = logging.getLogger(__name__)

def create_grupo_instructor(db: Session, grupo_instructor: GrupoInstructorCreate):
    try:
        query = text("""
            INSERT INTO grupo_instructor (cod_ficha, id_instructor)
            VALUES (:cod_ficha, :id_instructor)
        """)
        db.execute(query, grupo_instructor.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al asignar instructor a grupo: {e}")
        raise

def update_grupo_instructor(db: Session, cod_ficha_actual: int, id_instructor_actual: int, grupo_instructor_update: GrupoInstructorUpdate):
    try:
        query = text("""
            UPDATE grupo_instructor
            SET cod_ficha = :cod_ficha, id_instructor = :id_instructor
            WHERE cod_ficha = :cod_ficha_actual AND id_instructor = :id_instructor_actual
        """)
        db.execute(query, {
            "cod_ficha": grupo_instructor_update.cod_ficha,
            "id_instructor": grupo_instructor_update.id_instructor,
            "cod_ficha_actual": cod_ficha_actual,
            "id_instructor_actual": id_instructor_actual
        })
        db.commit()
        # Devolver el registro actualizado
        return {
            "cod_ficha": grupo_instructor_update.cod_ficha,
            "id_instructor": grupo_instructor_update.id_instructor
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar instructor de grupo: {e}")
        raise

def get_instructores_by_grupo(db: Session, cod_ficha: int):
    try:
        query = text("SELECT * FROM grupo_instructor WHERE cod_ficha = :cod_ficha")
        result = db.execute(query, {"cod_ficha": cod_ficha}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener instructores del grupo: {e}")
        raise

def get_grupos_by_instructor(db: Session, id_instructor: int):
    try:
        query = text("SELECT * FROM grupo_instructor WHERE id_instructor = :id_instructor")
        result = db.execute(query, {"id_instructor": id_instructor}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener grupos del instructor: {e}")
        raise

def delete_grupo_instructor(db: Session, cod_ficha: int, id_instructor: int):
    try:
        query = text("""
            DELETE FROM grupo_instructor
            WHERE cod_ficha = :cod_ficha AND id_instructor = :id_instructor
        """)
        result = db.execute(query, {"cod_ficha": cod_ficha, "id_instructor": id_instructor})
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar instructor de grupo: {e}")
        raise