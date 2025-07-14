from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import logging
import pandas as pd
from app.schemas import grupos as schemas

logger = logging.getLogger(__name__)

def upsert_regional(db: Session, regional: schemas.RegionalCreate):
    """
    Inserta o actualiza una regional en la base de datos.
    """
    try:
        query = text("""
            INSERT INTO regional (cod_regional, nombre)
            VALUES (:cod_regional, :nombre)
            ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
        """)
        db.execute(query, regional.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al hacer upsert de regional: {e}")
        raise Exception("Error de base de datos al procesar regional")

def upsert_centro_formacion(db: Session, centro: schemas.CentroFormacionCreate):
    """
    Inserta o actualiza un centro de formación en la base de datos.
    """
    try:
        query = text("""
            INSERT INTO centro_formacion (cod_centro, nombre_centro, cod_regional)
            VALUES (:cod_centro, :nombre_centro, :cod_regional)
            ON DUPLICATE KEY UPDATE 
                nombre_centro = VALUES(nombre_centro),
                cod_regional = VALUES(cod_regional)
        """)
        db.execute(query, centro.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al hacer upsert de centro de formación: {e}")
        raise Exception("Error de base de datos al procesar centro de formación")

def upsert_programas_formacion_bulk(db: Session, df_programas: pd.DataFrame):
    """
    Inserta o actualiza programas de formación en la base de datos de forma masiva.
    """
    programas_insertados = 0
    programas_actualizados = 0
    errores = []

    insert_programa_sql = text("""
        INSERT INTO programa_formacion (
            cod_programa, la_version, nombre, horas_lectivas, horas_productivas
        ) VALUES (
            :cod_programa, :la_version, :nombre, :horas_lectivas, :horas_productivas
        )
        ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
    """)

    for idx, row in df_programas.iterrows():
        try:
            db.execute(insert_programa_sql, row.to_dict())
            programas_insertados += 1  # Contamos como inserción exitosa
        except SQLAlchemyError as e:
            msg = f"Error al insertar programa (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar programa: {e}")

    db.commit()
    return {
        "programas_insertados": programas_insertados,
        "programas_actualizados": programas_actualizados,
        "errores": errores
    }

def upsert_grupos_bulk(db: Session, df: pd.DataFrame):
    """
    Inserta o actualiza grupos en la base de datos de forma masiva.
    """
    grupos_insertados = 0
    grupos_actualizados = 0
    errores = []

    insert_grupo_sql = text("""
        INSERT INTO grupo (
            cod_ficha, cod_centro, cod_programa, la_version, estado_grupo,
            nombre_nivel, jornada, fecha_inicio, fecha_fin, etapa,
            modalidad, responsable, nombre_empresa, nombre_municipio,
            nombre_programa_especial, hora_inicio, hora_fin
        ) VALUES (
            :cod_ficha, :cod_centro, :cod_programa, :la_version, :estado_grupo,
            :nombre_nivel, :jornada, :fecha_inicio, :fecha_fin, :etapa,
            :modalidad, :responsable, :nombre_empresa, :nombre_municipio,
            :nombre_programa_especial, :hora_inicio, :hora_fin
        )
        ON DUPLICATE KEY UPDATE
            cod_centro = VALUES(cod_centro),
            cod_programa = VALUES(cod_programa),
            la_version = VALUES(la_version),
            estado_grupo = VALUES(estado_grupo),
            nombre_nivel = VALUES(nombre_nivel),
            jornada = VALUES(jornada),
            fecha_inicio = VALUES(fecha_inicio),
            fecha_fin = VALUES(fecha_fin),
            etapa = VALUES(etapa),
            modalidad = VALUES(modalidad),
            responsable = VALUES(responsable),
            nombre_empresa = VALUES(nombre_empresa),
            nombre_municipio = VALUES(nombre_municipio),
            nombre_programa_especial = VALUES(nombre_programa_especial),
            hora_inicio = VALUES(hora_inicio),
            hora_fin = VALUES(hora_fin)
    """)

    for idx, row in df.iterrows():
        try:
            result = db.execute(insert_grupo_sql, row.to_dict())
            if result.rowcount == 1:
                grupos_insertados += 1
            elif result.rowcount == 2:
                grupos_actualizados += 1
        except SQLAlchemyError as e:
            msg = f"Error al insertar grupo (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar grupo: {e}")

    db.commit()
    return {
        "grupos_insertados": grupos_insertados,
        "grupos_actualizados": grupos_actualizados,
        "errores": errores
    }

def upsert_datos_grupo_bulk(db: Session, df_datos_grupo: pd.DataFrame):
    """
    Inserta o actualiza datos de grupo en la base de datos de forma masiva.
    """
    datos_insertados = 0
    datos_actualizados = 0
    errores = []

    insert_datos_sql = text("""
        INSERT INTO datos_grupo (
            cod_ficha, num_aprendices_masculinos, num_aprendices_femenino,
            num_aprendices_no_binario, num_total_aprendices, num_total_aprendices_activos
        ) VALUES (
            :cod_ficha, :num_aprendices_masculinos, :num_aprendices_femenino,
            :num_aprendices_no_binario, :num_total_aprendices, :num_total_aprendices_activos
        )
        ON DUPLICATE KEY UPDATE
            num_aprendices_masculinos = VALUES(num_aprendices_masculinos),
            num_aprendices_femenino = VALUES(num_aprendices_femenino),
            num_aprendices_no_binario = VALUES(num_aprendices_no_binario),
            num_total_aprendices = VALUES(num_total_aprendices),
            num_total_aprendices_activos = VALUES(num_total_aprendices_activos)
    """)

    for idx, row in df_datos_grupo.iterrows():
        try:
            # Filtrar solo las columnas necesarias y con valores no nulos
            data_dict = {
                'cod_ficha': row['cod_ficha'],
                'num_aprendices_masculinos': row.get('num_aprendices_masculinos'),
                'num_aprendices_femenino': row.get('num_aprendices_femenino'),
                'num_aprendices_no_binario': row.get('num_aprendices_no_binario'),
                'num_total_aprendices': row.get('num_total_aprendices'),
                'num_total_aprendices_activos': row.get('num_total_aprendices_activos')
            }
            
            db.execute(insert_datos_sql, data_dict)
            datos_insertados += 1  # Contamos como inserción exitosa
        except SQLAlchemyError as e:
            msg = f"Error al insertar datos de grupo (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar datos de grupo: {e}")

    db.commit()
    return {
        "datos_insertados": datos_insertados,
        "datos_actualizados": datos_actualizados,
        "errores": errores
    }

def insertar_datos_en_bd(db: Session, df_programas, df):
    """
    Función legacy mantenida para compatibilidad. 
    Se recomienda usar las funciones upsert específicas.
    """
    programas_insertados = 0
    programas_actualizados = 0
    grupos_insertados = 0
    grupos_actualizados = 0
    errores = []

    # 1. Insertar programas
    insert_programa_sql = text("""
        INSERT INTO programa_formacion (
            cod_programa, la_version, nombre, horas_lectivas, horas_productivas
        ) VALUES (
            :cod_programa, :la_version, :nombre, :horas_lectivas, :horas_productivas
        )
        ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
    """)

    for idx, row in df_programas.iterrows():
        try:
            result = db.execute(insert_programa_sql, row.to_dict())
            rowcount = result.rowcount or 0
            if rowcount == 1:
                programas_insertados += 1
            elif rowcount == 2:
                programas_actualizados += 1
        except SQLAlchemyError as e:
            msg = f"Error al insertar programa (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar: {e}")

    # 2. Insertar grupos
    insert_grupo_sql = text("""
        INSERT INTO grupo (
            cod_ficha, cod_centro, cod_programa, la_version, estado_grupo,
            nombre_nivel, jornada, fecha_inicio, fecha_fin, etapa,
            modalidad, responsable, nombre_empresa, nombre_municipio,
            nombre_programa_especial, hora_inicio, hora_fin
        ) VALUES (
            :cod_ficha, :cod_centro, :cod_programa, :la_version, :estado_grupo,
            :nombre_nivel, :jornada, :fecha_inicio, :fecha_fin, :etapa,
            :modalidad, :responsable, :nombre_empresa, :nombre_municipio,
            :nombre_programa_especial, :hora_inicio, :hora_fin
        )
        ON DUPLICATE KEY UPDATE
            estado_grupo=VALUES(estado_grupo),
            etapa=VALUES(etapa),
            responsable=VALUES(responsable),
            nombre_programa_especial=VALUES(nombre_programa_especial),
            hora_inicio=VALUES(hora_inicio),
            hora_fin=VALUES(hora_fin)
    """)

    for idx, row in df.iterrows():
        try:
            result = db.execute(insert_grupo_sql, row.to_dict())
            rowcount = result.rowcount or 0
            if rowcount == 1:
                grupos_insertados += 1
            elif rowcount == 2:
                grupos_actualizados += 1
        except SQLAlchemyError as e:
            msg = f"Error al insertar grupo (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar: {e}")

    # Confirmar cambios
    db.commit()

    return {
        "programas_insertados": programas_insertados,
        "programas_actualizados": programas_actualizados,
        "grupos_insertados": grupos_insertados,
        "grupos_actualizados": grupos_actualizados,
        "errores": errores,
        "mensaje": "Carga completada con errores" if errores else "Carga completada exitosamente"
    }
