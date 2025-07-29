from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def get_festivos(db: Session) -> List[date]:
    """
    Obtiene todos los días festivos de la base de datos.
    
    Args:
        db: Sesión de la base de datos
        
    Returns:
        List[date]: Lista de fechas festivas
    """
    try:
        query = text("SELECT festivo FROM festivos ORDER BY festivo")
        result = db.execute(query).fetchall()
        return [row[0] for row in result]
    except Exception as e:
        logger.error(f"Error al obtener festivos: {e}")
        raise Exception("Error de base de datos al obtener los festivos")

def get_domingos_in_range(start_date: date, end_date: date) -> List[date]:
    """
    Genera una lista de todos los domingos en un rango de fechas.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        List[date]: Lista de fechas que son domingos
    """
    domingos = []
    current_date = start_date
    
    # Encontrar el primer domingo en el rango
    while current_date.weekday() != 6:  # 6 = domingo
        current_date += timedelta(days=1)
        if current_date > end_date:
            return domingos
    
    # Agregar todos los domingos
    while current_date <= end_date:
        domingos.append(current_date)
        current_date += timedelta(days=7)
    
    return domingos

def get_festivos_y_domingos(db: Session, year: int = None) -> Dict[str, any]:
    """
    Obtiene todos los festivos de la base de datos y los domingos del año especificado.
    
    Args:
        db: Sesión de la base de datos
        year: Año para filtrar (opcional, por defecto año actual)
        
    Returns:
        Dict con festivos, domingos y total de días
    """
    try:
        # Obtener festivos de la base de datos
        if year:
            query = text("SELECT festivo FROM festivos WHERE YEAR(festivo) = :year ORDER BY festivo")
            result = db.execute(query, {"year": year}).fetchall()
        else:
            query = text("SELECT festivo FROM festivos ORDER BY festivo")
            result = db.execute(query).fetchall()
        
        festivos = [row[0] for row in result]
        
        # Si se especifica un año, obtener domingos de ese año
        if year:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            domingos = get_domingos_in_range(start_date, end_date)
        else:
            # Si no se especifica año, obtener domingos del año actual
            current_year = date.today().year
            start_date = date(current_year, 1, 1)
            end_date = date(current_year, 12, 31)
            domingos = get_domingos_in_range(start_date, end_date)
        
        return {
            "festivos": festivos,
            "domingos": domingos,
            "total_dias": len(festivos) + len(domingos)
        }
        
    except Exception as e:
        logger.error(f"Error al obtener festivos y domingos: {e}")
        raise Exception("Error de base de datos al obtener festivos y domingos")

def get_festivos_by_year(db: Session, year: int) -> List[date]:
    """
    Obtiene los festivos de un año específico.
    
    Args:
        db: Sesión de la base de datos
        year: Año para filtrar
        
    Returns:
        List[date]: Lista de fechas festivas del año especificado
    """
    try:
        query = text("SELECT festivo FROM festivos WHERE YEAR(festivo) = :year ORDER BY festivo")
        result = db.execute(query, {"year": year}).fetchall()
        return [row[0] for row in result]
    except Exception as e:
        logger.error(f"Error al obtener festivos por año: {e}")
        raise Exception("Error de base de datos al obtener los festivos por año")
