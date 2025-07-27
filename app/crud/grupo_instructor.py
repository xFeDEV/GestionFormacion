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
    """
    Obtiene todos los instructores asignados a un grupo con información detallada.
    """
    try:
        query = text("""
            SELECT 
                gi.cod_ficha,
                gi.id_instructor,
                u.nombre_completo,
                u.correo,
                u.identificacion,
                u.telefono,
                u.tipo_contrato,
                r.nombre as nombre_rol
            FROM grupo_instructor gi
            INNER JOIN usuario u ON gi.id_instructor = u.id_usuario
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE gi.cod_ficha = :cod_ficha
            ORDER BY u.nombre_completo
        """)
        result = db.execute(query, {"cod_ficha": cod_ficha}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener instructores del grupo: {e}")
        raise Exception("Error de base de datos al obtener instructores del grupo")

def get_grupos_by_instructor(db: Session, id_instructor: int):
    """
    Obtiene todos los grupos asignados a un instructor con información detallada.
    """
    try:
        query = text("""
            SELECT 
                gi.cod_ficha,
                gi.id_instructor,
                g.estado_grupo,
                g.jornada,
                g.fecha_inicio,
                g.fecha_fin,
                g.etapa,
                pf.nombre as nombre_programa,
                cf.nombre_centro
            FROM grupo_instructor gi
            INNER JOIN grupo g ON gi.cod_ficha = g.cod_ficha
            INNER JOIN programa_formacion pf ON g.cod_programa = pf.cod_programa 
                AND g.la_version = pf.la_version
            INNER JOIN centro_formacion cf ON g.cod_centro = cf.cod_centro
            WHERE gi.id_instructor = :id_instructor
            ORDER BY g.fecha_inicio DESC
        """)
        result = db.execute(query, {"id_instructor": id_instructor}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener grupos del instructor: {e}")
        raise Exception("Error de base de datos al obtener grupos del instructor")

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