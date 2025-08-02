from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from app.schemas.programacion import ProgramacionCreate, ProgramacionUpdate
from app.crud import notificacion as crud_notificacion
from app.schemas.notificacion import NotificacionCreate
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

def create_programacion(db: Session, programacion: ProgramacionCreate, id_user: int) -> Optional[dict]:
    """
    Crea una nueva programación.
    """
    try:
        # Verificar conflictos de horarios antes del INSERT
        verificacion_query = text("""
            SELECT COUNT(*) as conflictos
            FROM programacion 
            WHERE id_instructor = :id_instructor 
              AND fecha_programada = :fecha_programada
              AND ((:hora_inicio < hora_fin) AND (:hora_fin > hora_inicio))
        """)
        
        verificacion_params = {
            "id_instructor": programacion.id_instructor,
            "fecha_programada": programacion.fecha_programada,
            "hora_inicio": programacion.hora_inicio,
            "hora_fin": programacion.hora_fin
        }
        
        resultado_verificacion = db.execute(verificacion_query, verificacion_params).mappings().first()
        
        if resultado_verificacion and resultado_verificacion['conflictos'] > 0:
            raise HTTPException(
                status_code=409, 
                detail="El instructor ya tiene una programación que se cruza en este horario"
            )
        
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
        
        # Crear notificación para el instructor
        try:
            # Obtener detalles adicionales para el mensaje de notificación
            notification_query = text("""
                SELECT p.cod_ficha, p.fecha_programada, p.hora_inicio, p.hora_fin,
                       c.nombre as nombre_competencia
                FROM programacion p
                LEFT JOIN competencia c ON p.cod_competencia = c.cod_competencia
                WHERE p.id_programacion = :id_programacion
            """)
            programacion_details = db.execute(notification_query, {"id_programacion": id_programacion}).mappings().first()
            
            if programacion_details:
                # Construir mensaje descriptivo
                mensaje = (f"Has sido asignado a la ficha {programacion_details['cod_ficha']} "
                          f"en la competencia {programacion_details['nombre_competencia']} "
                          f"para el día {programacion_details['fecha_programada']} "
                          f"de {programacion_details['hora_inicio']} a {programacion_details['hora_fin']}.")
                
                # Crear la notificación
                nueva_notificacion = NotificacionCreate(
                    id_usuario=programacion.id_instructor,
                    mensaje=mensaje,
                    leida=False
                )
                
                # Guardar la notificación
                crud_notificacion.create_notification(db=db, notificacion=nueva_notificacion)
                
        except Exception as notif_error:
            # Log del error pero no fallar la creación de programación
            logger.warning(f"Error al crear notificación para programación {id_programacion}: {notif_error}")
        
        # Retornar la programación creada
        return get_programacion_by_id(db, id_programacion)
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
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
        
        # Verificar conflictos de horarios antes del UPDATE (solo si se modifican datos relacionados con horarios)
        if any(field in fields for field in ['id_instructor', 'fecha_programada', 'hora_inicio', 'hora_fin']):
            # Obtener datos actuales de la programación para completar la verificación
            current_data_query = text("""
                SELECT id_instructor, fecha_programada, hora_inicio, hora_fin
                FROM programacion 
                WHERE id_programacion = :id_programacion
            """)
            current_data = db.execute(current_data_query, {"id_programacion": id_programacion}).mappings().first()
            
            if current_data:
                # Usar los valores nuevos si están en fields, sino usar los actuales
                id_instructor = fields.get('id_instructor', current_data['id_instructor'])
                fecha_programada = fields.get('fecha_programada', current_data['fecha_programada'])
                hora_inicio = fields.get('hora_inicio', current_data['hora_inicio'])
                hora_fin = fields.get('hora_fin', current_data['hora_fin'])
                
                verificacion_query = text("""
                    SELECT COUNT(*) as conflictos
                    FROM programacion 
                    WHERE id_instructor = :id_instructor 
                      AND fecha_programada = :fecha_programada
                      AND id_programacion != :id_programacion_actual
                      AND ((:hora_inicio < hora_fin) AND (:hora_fin > hora_inicio))
                """)
                
                verificacion_params = {
                    "id_instructor": id_instructor,
                    "fecha_programada": fecha_programada,
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                    "id_programacion_actual": id_programacion
                }
                
                resultado_verificacion = db.execute(verificacion_query, verificacion_params).mappings().first()
                
                if resultado_verificacion and resultado_verificacion['conflictos'] > 0:
                    raise HTTPException(
                        status_code=409, 
                        detail="El instructor ya tiene una programación que se cruza en este horario"
                    )
        
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
        if isinstance(e, HTTPException):
            raise e
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