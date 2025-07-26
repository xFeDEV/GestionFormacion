from ast import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.grupos import GrupoUpdate
from typing import Optional, List
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
    

def get_grupos_by_cod_centro(db: Session, cod_centro: int) -> List[dict]:
    """
    Obtiene todos los grupos que pertenecen a un centro de formación específico.
    """
    try:
        query = text("SELECT * FROM grupo WHERE cod_centro = :cod_centro")
        result = db.execute(query, {"cod_centro": cod_centro}).mappings().all()
        return result
    except Exception as e:
        logger.error(f"Error al obtener los grupos por el centro {cod_centro}: {e}")
        raise Exception("Error de base de datos al obtener el grupo por centro")   


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

def search_grupos_for_select(db: Session, search_text: str = "", limit: int = 20) -> List[dict]:
    """
    Busca grupos para usar en un select/autocompletar.
    Retorna información básica de los grupos que coincidan con el texto de búsqueda.
    """
    try:
        # Si no hay texto de búsqueda, obtener todos los grupos activos
        if not search_text.strip():
            query = text("""
                SELECT 
                    g.cod_ficha,
                    g.estado_grupo,
                    g.jornada,
                    g.fecha_inicio,
                    g.fecha_fin,
                    g.etapa,
                    pf.nombre as nombre_programa
                FROM grupo g
                LEFT JOIN programa_formacion pf ON g.cod_programa = pf.cod_programa AND g.la_version = pf.la_version
                WHERE g.estado_grupo NOT IN ('CANCELADO', 'CERRADO')
                ORDER BY g.cod_ficha DESC
                LIMIT :limit
            """)
            result = db.execute(query, {"limit": limit}).mappings().all()
        else:
            # Detectar si es búsqueda numérica (código de ficha) o texto (nombre programa)
            is_numeric_search = search_text.strip().isdigit()
            
            if is_numeric_search:
                # Para códigos numéricos: buscar solo códigos que EMPIECEN con el número
                search_pattern = f"{search_text}%"
                query = text("""
                    SELECT 
                        g.cod_ficha,
                        g.estado_grupo,
                        g.jornada,
                        g.fecha_inicio,
                        g.fecha_fin,
                        g.etapa,
                        pf.nombre as nombre_programa
                    FROM grupo g
                    LEFT JOIN programa_formacion pf ON g.cod_programa = pf.cod_programa AND g.la_version = pf.la_version
                    WHERE CAST(g.cod_ficha AS CHAR) LIKE :search_pattern
                    AND g.estado_grupo NOT IN ('CANCELADO', 'CERRADO')
                    ORDER BY g.cod_ficha ASC
                    LIMIT :limit
                """)
                result = db.execute(query, {
                    "search_pattern": search_pattern, 
                    "limit": limit
                }).mappings().all()
            else:
                # Para texto: buscar en nombre de programa con coincidencia parcial
                search_pattern = f"%{search_text}%"
                query = text("""
                    SELECT 
                        g.cod_ficha,
                        g.estado_grupo,
                        g.jornada,
                        g.fecha_inicio,
                        g.fecha_fin,
                        g.etapa,
                        pf.nombre as nombre_programa
                    FROM grupo g
                    LEFT JOIN programa_formacion pf ON g.cod_programa = pf.cod_programa AND g.la_version = pf.la_version
                    WHERE UPPER(pf.nombre) LIKE UPPER(:search_pattern)
                    AND g.estado_grupo NOT IN ('CANCELADO', 'CERRADO')
                    ORDER BY 
                        CASE WHEN UPPER(pf.nombre) LIKE UPPER(:exact_pattern) THEN 1 ELSE 2 END,
                        g.cod_ficha DESC
                    LIMIT :limit
                """)
                exact_pattern = f"{search_text}%"
                result = db.execute(query, {
                    "search_pattern": search_pattern,
                    "exact_pattern": exact_pattern,
                    "limit": limit
                }).mappings().all()
        
        return result
    except Exception as e:
        logger.error(f"Error al buscar grupos: {e}")
        raise Exception("Error de base de datos al buscar grupos")
