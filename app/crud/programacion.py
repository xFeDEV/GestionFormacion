from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.programacion import ProgramacionCreate, ProgramacionUpdate
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

def create_programacion(db: Session, programacion: ProgramacionCreate, id_user: int) -> Optional[dict]:
    """
    Crea una nueva programación.
    """
    try:
        query = text("""
            INSERT INTO programacion 
            (id_instructor, cod_ficha, fecha_programada, horas_programadas, 
             hora_inicio, hora_fin, cod_competencia, cod_resultado, id_user)
            VALUES (:id_instructor, :cod_ficha, :fecha_programada, :horas_programadas,
                    :hora_inicio, :hora_fin, :cod_competencia, :cod_resultado, :id_user)
        """)
        
        params = {
            "id_instructor": programacion.id_instructor,
            "cod_ficha": programacion.cod_ficha,
            "fecha_programada": programacion.fecha_programada,
            "horas_programadas": programacion.horas_programadas,
            "hora_inicio": programacion.hora_inicio,
            "hora_fin": programacion.hora_fin,
            "cod_competencia": programacion.cod_competencia,
            "cod_resultado": programacion.cod_resultado,
            "id_user": id_user
        }
        
        result = db.execute(query, params)
        db.commit()
        
        # Obtener el ID de la programación recién creada
        id_programacion = result.lastrowid
        
        # Retornar la programación creada
        return get_programacion_by_id(db, id_programacion)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear la programación: {e}")
        raise Exception("Error de base de datos al crear la programación")

def get_programacion_by_id(db: Session, id_programacion: int) -> Optional[dict]:
    """
    Obtiene una programación específica por su ID con información completa.
    """
    try:
        query = text("""
            SELECT p.*, 
                   u.nombre_completo as nombre_instructor,
                   c.nombre as nombre_competencia,
                   r.nombre as nombre_resultado
            FROM programacion p
            LEFT JOIN usuario u ON p.id_instructor = u.id_usuario
            LEFT JOIN competencia c ON p.cod_competencia = c.cod_competencia
            LEFT JOIN resultado_aprendizaje r ON p.cod_resultado = r.cod_resultado
            WHERE p.id_programacion = :id_programacion
        """)
        result = db.execute(query, {"id_programacion": id_programacion}).mappings().first()
        return result
    except Exception as e:
        logger.error(f"Error al obtener la programación {id_programacion}: {e}")
        raise Exception("Error de base de datos al obtener la programación")

def get_programaciones_by_ficha(db: Session, cod_ficha: int) -> List[dict]:
    """
    Obtiene todas las programaciones de un grupo específico.
    """
    try:
        query = text("""
            SELECT p.*, 
                   u.nombre_completo as nombre_instructor,
                   c.nombre as nombre_competencia,
                   r.nombre as nombre_resultado
            FROM programacion p
            LEFT JOIN usuario u ON p.id_instructor = u.id_usuario
            LEFT JOIN competencia c ON p.cod_competencia = c.cod_competencia
            LEFT JOIN resultado_aprendizaje r ON p.cod_resultado = r.cod_resultado
            WHERE p.cod_ficha = :cod_ficha
            ORDER BY p.fecha_programada, p.hora_inicio
        """)
        result = db.execute(query, {"cod_ficha": cod_ficha}).mappings().all()
        return result
    except Exception as e:
        logger.error(f"Error al obtener las programaciones del grupo {cod_ficha}: {e}")
        raise Exception("Error de base de datos al obtener las programaciones del grupo")

def get_programaciones_by_instructor(db: Session, id_instructor: int) -> List[dict]:
    """
    Obtiene todas las programaciones de un instructor específico.
    """
    try:
        query = text("""
            SELECT p.*, 
                   u.nombre_completo as nombre_instructor,
                   c.nombre as nombre_competencia,
                   r.nombre as nombre_resultado
            FROM programacion p
            LEFT JOIN usuario u ON p.id_instructor = u.id_usuario
            LEFT JOIN competencia c ON p.cod_competencia = c.cod_competencia
            LEFT JOIN resultado_aprendizaje r ON p.cod_resultado = r.cod_resultado
            WHERE p.id_instructor = :id_instructor
            ORDER BY p.fecha_programada, p.hora_inicio
        """)
        result = db.execute(query, {"id_instructor": id_instructor}).mappings().all()
        return result
    except Exception as e:
        logger.error(f"Error al obtener las programaciones del instructor {id_instructor}: {e}")
        raise Exception("Error de base de datos al obtener las programaciones del instructor")

def update_programacion(db: Session, id_programacion: int, programacion: ProgramacionUpdate) -> bool:
    """
    Actualiza una programación existente.
    """
    try:
        # Obtiene solo los campos que el usuario envió en la petición
        fields = programacion.model_dump(exclude_unset=True)

        # Si no se envió ningún dato para actualizar, no hace nada
        if not fields:
            return False
        
        # Construye la parte SET de la consulta SQL dinámicamente
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])

        # Agrega el id_programacion para el WHERE
        params = {"id_programacion": id_programacion, **fields}
        
        query = text(f"UPDATE programacion SET {set_clause} WHERE id_programacion = :id_programacion")
        
        result = db.execute(query, params)
        db.commit()
        
        return result.rowcount > 0
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar la programación: {e}")
        raise Exception("Error de base de datos al actualizar la programación")

def delete_programacion(db: Session, id_programacion: int) -> bool:
    """
    Elimina una programación específica.
    """
    try:
        query = text("DELETE FROM programacion WHERE id_programacion = :id_programacion")
        result = db.execute(query, {"id_programacion": id_programacion})
        db.commit()
        
        return result.rowcount > 0
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar la programación {id_programacion}: {e}")
        raise Exception("Error de base de datos al eliminar la programación")

def get_all_programaciones(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Obtiene todas las programaciones con paginación.
    """
    try:
        query = text("""
            SELECT p.*, 
                   u.nombre_completo as nombre_instructor,
                   c.nombre as nombre_competencia,
                   r.nombre as nombre_resultado
            FROM programacion p
            LEFT JOIN usuario u ON p.id_instructor = u.id_usuario
            LEFT JOIN competencia c ON p.cod_competencia = c.cod_competencia
            LEFT JOIN resultado_aprendizaje r ON p.cod_resultado = r.cod_resultado
            ORDER BY p.fecha_programada DESC, p.hora_inicio
            LIMIT :limit OFFSET :skip
        """)
        result = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
        return result
    except Exception as e:
        logger.error(f"Error al obtener todas las programaciones: {e}")
        raise Exception("Error de base de datos al obtener las programaciones")

def get_competencias_by_programa(db: Session, cod_programa: int, la_version: int = None) -> List[dict]:
    """
    Obtiene las competencias asociadas a un programa de formación específico.
    Nota: Las competencias están asociadas al programa, no a una versión específica.
    """
    try:
        query = text("""
            SELECT DISTINCT c.cod_competencia, c.nombre, c.horas
            FROM competencia c
            INNER JOIN programa_competencia pc ON c.cod_competencia = pc.cod_competencia
            WHERE pc.cod_programa = :cod_programa
            ORDER BY c.nombre
        """)
        result = db.execute(query, {"cod_programa": cod_programa}).mappings().all()
        return result
    except Exception as e:
        logger.error(f"Error al obtener competencias del programa {cod_programa}: {e}")
        raise Exception("Error de base de datos al obtener las competencias del programa")

def get_resultados_by_competencia(db: Session, cod_competencia: int) -> List[dict]:
    """
    Obtiene los resultados de aprendizaje para una competencia específica.
    """
    try:
        query = text("""
            SELECT cod_resultado, nombre, cod_competencia, 0 as horas
            FROM resultado_aprendizaje
            WHERE cod_competencia = :cod_competencia
            ORDER BY nombre
        """)
        result = db.execute(query, {"cod_competencia": cod_competencia}).mappings().all()
        return result
    except Exception as e:
        logger.error(f"Error al obtener resultados de la competencia {cod_competencia}: {e}")
        raise Exception("Error de base de datos al obtener los resultados de aprendizaje") 