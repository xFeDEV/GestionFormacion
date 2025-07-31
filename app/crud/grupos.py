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

# --- Funciones para el Dashboard con Filtros ---

def _build_dynamic_where_clause(
    cod_centro: int,
    estado_grupo: Optional[str] = None,
    nombre_nivel: Optional[str] = None,
    etapa: Optional[str] = None,
    modalidad: Optional[str] = None,
    jornada: Optional[str] = None,
    nombre_municipio: Optional[str] = None,
    año: Optional[int] = None
) -> tuple[str, dict]:
    """Función auxiliar para construir cláusulas WHERE dinámicas y seguras."""
    conditions = ["g.cod_centro = :cod_centro"]
    params = {"cod_centro": cod_centro}
    
    if estado_grupo is not None:
        conditions.append("g.estado_grupo = :estado_grupo")
        params["estado_grupo"] = estado_grupo

    if nombre_nivel is not None:
        conditions.append("g.nombre_nivel = :nombre_nivel")
        params["nombre_nivel"] = nombre_nivel

    if etapa is not None:
        conditions.append("g.etapa = :etapa")
        params["etapa"] = etapa

    if modalidad is not None:
        conditions.append("g.modalidad = :modalidad")
        params["modalidad"] = modalidad

    if jornada is not None:
        conditions.append("g.jornada = :jornada")
        params["jornada"] = jornada

    if nombre_municipio is not None:
        conditions.append("g.nombre_municipio = :nombre_municipio")
        params["nombre_municipio"] = nombre_municipio

    if año is not None:
        conditions.append("YEAR(g.fecha_inicio) = :año")
        params["año"] = año
            
    return "WHERE " + " AND ".join(conditions), params

def get_dashboard_kpis(db: Session, cod_centro: int, estado_grupo: Optional[str] = None, nombre_nivel: Optional[str] = None, etapa: Optional[str] = None, modalidad: Optional[str] = None, jornada: Optional[str] = None, nombre_municipio: Optional[str] = None, año: Optional[int] = None) -> dict:
    """
    Calcula el número total de grupos basado en filtros obligatorios y un año opcional.
    """
    try:
        where_clause, params = _build_dynamic_where_clause(cod_centro, estado_grupo, nombre_nivel, etapa, modalidad, jornada, nombre_municipio, año)
        query = text(f"SELECT COUNT(cod_ficha) as total_grupo FROM grupo g {where_clause}")
        
        # .scalar() es ideal para obtener un único valor de una consulta
        total = db.execute(query, params).scalar() or 0
        return {"total_grupo": total}
    except Exception as e:
        logger.error(f"Error al calcular KPIs del dashboard: {e}")
        raise Exception("Error de base de datos al calcular KPIs")

def get_grupos_por_municipio_filtrado(db: Session, cod_centro: int, estado_grupo: str, nombre_nivel: Optional[str] = None, etapa: Optional[str] = None, modalidad: Optional[str] = None, jornada: Optional[str] = None, nombre_municipio: Optional[str] = None, año: Optional[int] = None) -> List[dict]:
    try:
        where_clause, params = _build_dynamic_where_clause(cod_centro, estado_grupo, nombre_nivel, etapa, modalidad, jornada, nombre_municipio, año)
        query_str = f"""
            SELECT nombre_municipio AS municipio, COUNT(cod_ficha) AS cantidad
            FROM grupo g {where_clause}
            GROUP BY nombre_municipio ORDER BY cantidad DESC
        """
        return db.execute(text(query_str), params).mappings().all()
    except Exception as e:
        logger.error(f"Error al obtener grupos filtrados por municipio: {e}")
        raise Exception("Error de base de datos al agrupar por municipio")

def get_grupos_por_jornada_filtrado(db: Session, cod_centro: int, estado_grupo: str, nombre_nivel: Optional[str] = None, etapa: Optional[str] = None, modalidad: Optional[str] = None, jornada: Optional[str] = None, nombre_municipio: Optional[str] = None, año: Optional[int] = None) -> List[dict]:
    try:
        where_clause, params = _build_dynamic_where_clause(cod_centro, estado_grupo, nombre_nivel, etapa, modalidad, jornada, nombre_municipio, año)
        query_str = f"""
            SELECT jornada, COUNT(cod_ficha) AS cantidad
            FROM grupo g {where_clause}
            GROUP BY jornada ORDER BY cantidad DESC
        """
        return db.execute(text(query_str), params).mappings().all()
    except Exception as e:
        logger.error(f"Error al obtener grupos filtrados por jornada: {e}")
        raise Exception("Error de base de datos al agrupar por jornada")

def get_grupos_por_modalidad_filtrado(db: Session, cod_centro: int, estado_grupo: str, nombre_nivel: Optional[str] = None, etapa: Optional[str] = None, modalidad: Optional[str] = None, jornada: Optional[str] = None, nombre_municipio: Optional[str] = None, año: Optional[int] = None) -> List[dict]:
    try:
        where_clause, params = _build_dynamic_where_clause(cod_centro, estado_grupo, nombre_nivel, etapa, modalidad, jornada, nombre_municipio, año)
        query_str = f"""
            SELECT modalidad, COUNT(cod_ficha) AS cantidad
            FROM grupo g {where_clause}
            GROUP BY modalidad ORDER BY cantidad DESC
        """
        return db.execute(text(query_str), params).mappings().all()
    except Exception as e:
        logger.error(f"Error al obtener grupos filtrados por modalidad: {e}")
        raise Exception("Error de base de datos al agrupar por modalidad")

def get_grupos_por_etapa_filtrado(db: Session, cod_centro: int, estado_grupo: str, nombre_nivel: Optional[str] = None, etapa: Optional[str] = None, modalidad: Optional[str] = None, jornada: Optional[str] = None, nombre_municipio: Optional[str] = None, año: Optional[int] = None) -> List[dict]:
    try:
        where_clause, params = _build_dynamic_where_clause(cod_centro, estado_grupo, nombre_nivel, etapa, modalidad, jornada, nombre_municipio, año)
        query_str = f"""
            SELECT etapa, COUNT(cod_ficha) AS cantidad
            FROM grupo g {where_clause}
            GROUP BY etapa ORDER BY cantidad DESC
        """
        return db.execute(text(query_str), params).mappings().all()
    except Exception as e:
        logger.error(f"Error al obtener grupos filtrados por etapa: {e}")
        raise Exception("Error de base de datos al agrupar por etapa")

def get_grupos_por_nivel_filtrado(db: Session, cod_centro: int, estado_grupo: str, nombre_nivel: Optional[str] = None, etapa: Optional[str] = None, modalidad: Optional[str] = None, jornada: Optional[str] = None, nombre_municipio: Optional[str] = None, año: Optional[int] = None) -> List[dict]:
    try:
        where_clause, params = _build_dynamic_where_clause(cod_centro, estado_grupo, nombre_nivel, etapa, modalidad, jornada, nombre_municipio, año)
        query_str = f"""
            SELECT nombre_nivel AS nivel, COUNT(cod_ficha) AS cantidad
            FROM grupo g {where_clause}
            GROUP BY nombre_nivel ORDER BY cantidad DESC
        """
        return db.execute(text(query_str), params).mappings().all()
    except Exception as e:
        logger.error(f"Error al obtener grupos filtrados por nivel: {e}")
        raise Exception("Error de base de datos al agrupar por nivel")