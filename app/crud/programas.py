from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
import logging
from app.schemas.programas import ProgramaCreate, ProgramaUpdate

logger = logging.getLogger(__name__)

def create_programa(db: Session, programa: ProgramaCreate) -> Optional[bool]:
    try:
        programa_data = programa.model_dump()
        query = text("""
            INSERT INTO programa_formacion (
                cod_programa, la_version, nombre,
                horas_lectivas, horas_productivas
            ) VALUES (
                :cod_programa, :la_version, :nombre,
                :horas_lectivas, :horas_productivas
            )
        """)
        db.execute(query, programa_data)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear programa: {e}")
        raise Exception("Error de base de datos al crear el programa")

def get_programa(db: Session, cod_programa: int):
    try:
        query = text("""
            SELECT cod_programa, la_version, nombre, horas_lectivas, horas_productivas
            FROM programa_formacion
            WHERE cod_programa = :cod_programa
            ORDER BY la_version DESC
        """)
        result = db.execute(query, {"cod_programa": cod_programa}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener programa: {e}")
        raise Exception("Error de base de datos al obtener el programa")

def get_programas(db: Session, skip: int = 0, limit: int = 20):
    try:
        # Consulta para obtener el conteo total
        count_query = text("SELECT COUNT(*) as total FROM programa_formacion")
        total_count = db.execute(count_query).scalar()
        
        # Consulta para obtener los programas paginados
        query = text("""
            SELECT cod_programa, la_version, nombre, horas_lectivas, horas_productivas
            FROM programa_formacion
            LIMIT :limit OFFSET :skip
        """)
        result = db.execute(query, {"limit": limit, "skip": skip}).mappings().all()
        
        return {
            "items": result,
            "total_items": total_count
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener programas: {e}")
        raise Exception("Error de base de datos al obtener los programas")

def search_programas(db: Session, search_term: str, skip: int = 0, limit: int = 20):
    try:
        # Añadir wildcards para la búsqueda LIKE
        search_pattern = f"%{search_term}%"
        
        # Consulta para obtener el conteo total de resultados de búsqueda
        count_query = text("""
            SELECT COUNT(*) as total 
            FROM programa_formacion 
            WHERE nombre LIKE :search_term
        """)
        total_count = db.execute(count_query, {"search_term": search_pattern}).scalar()
        
        # Consulta para obtener los programas paginados
        query = text("""
            SELECT cod_programa, la_version, nombre, horas_lectivas, horas_productivas
            FROM programa_formacion
            WHERE nombre LIKE :search_term
            LIMIT :limit OFFSET :skip
        """)
        result = db.execute(query, {
            "search_term": search_pattern, 
            "limit": limit, 
            "skip": skip
        }).mappings().all()
        
        return {
            "items": result,
            "total_items": total_count
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar programas: {e}")
        raise Exception("Error de base de datos al buscar los programas")

def update_programa(db: Session, cod_programa: int, programa_update: ProgramaUpdate) -> bool:
    try:
        fields = programa_update.model_dump(exclude_unset=True)
        if not fields:
            return False
        
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])
        
        fields["cod_programa"] = cod_programa

        query = text(f"""
            UPDATE programa_formacion 
            SET {set_clause} 
            WHERE cod_programa = :cod_programa AND la_version = (
                SELECT MAX(la_version) 
                FROM programa_formacion 
                WHERE cod_programa = :cod_programa
            )
        """)
        
        result = db.execute(query, fields)
        db.commit()
        
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar programa: {e}")
        raise Exception("Error de base de datos al actualizar el programa")

def delete_programa(db: Session, cod_programa: int, la_version: int) -> bool:
    try:
        query = text("""
            DELETE FROM programa_formacion 
            WHERE cod_programa = :cod_programa AND la_version = :la_version
        """)
        
        result = db.execute(query, {"cod_programa": cod_programa, "la_version": la_version})
        db.commit()
        
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar programa: {e}")
        raise Exception("Error de base de datos al eliminar el programa")
