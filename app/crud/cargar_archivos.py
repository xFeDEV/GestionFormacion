from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import logging
import pandas as pd
from app.schemas.centro_formacion import CentroFormacionCreate, CentroFormacionOut
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

def upsert_centro_formacion(db: Session, centro: CentroFormacionCreate):
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

def update_programas_duracion_bulk(db: Session, df_programas: pd.DataFrame):
    """
    Actualiza las duraciones de los programas de formación con datos del archivo DF-14.
    """
    programas_actualizados = 0
    errores = []

    update_programa_sql = text("""
        UPDATE programa_formacion 
        SET horas_lectivas = :horas_lectivas, 
            horas_productivas = :horas_productivas 
        WHERE cod_programa = :cod_programa AND la_version = :la_version
    """)

    for idx, row in df_programas.iterrows():
        try:
            # Filtrar solo los campos necesarios
            data_dict = {
                'cod_programa': row['cod_programa'],
                'la_version': row['la_version'],
                'horas_lectivas': row.get('horas_lectivas', 0),
                'horas_productivas': row.get('horas_productivas', 0)
            }
            
            db.execute(update_programa_sql, data_dict)
            programas_actualizados += 1
        except SQLAlchemyError as e:
            msg = f"Error al actualizar programa {row['cod_programa']}-{row['la_version']} (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al actualizar programa: {e}")

    db.commit()
    return {
        "programas_actualizados": programas_actualizados,
        "errores": errores
    }

def update_datos_grupo_bulk(db: Session, df_datos_grupo: pd.DataFrame):
    """
    Actualiza los datos de grupo con información del archivo DF-14.
    """
    datos_actualizados = 0
    errores = []

    update_datos_sql = text("""
        UPDATE datos_grupo 
        SET cupo_total = :cupo_total,
            en_transito = :en_transito,
            induccion = :induccion,
            formacion = :formacion,
            condicionado = :condicionado,
            aplazado = :aplazado,
            retiro_voluntario = :retiro_voluntario,
            cancelado = :cancelado,
            cancelamiento_vit_comp = :cancelamiento_vit_comp,
            desercion_vit_comp = :desercion_vit_comp,
            por_certificar = :por_certificar,
            certificados = :certificados,
            traslados = :traslados,
            otro = :otro
        WHERE cod_ficha = :cod_ficha
    """)

    for idx, row in df_datos_grupo.iterrows():
        try:
            # Preparar los datos para la actualización
            data_dict = {
                'cod_ficha': row['cod_ficha'],
                'cupo_total': row.get('cupo_total'),
                'en_transito': row.get('en_transito'),
                'induccion': row.get('induccion'),
                'formacion': row.get('formacion'),
                'condicionado': row.get('condicionado'),
                'aplazado': row.get('aplazado'),
                'retiro_voluntario': row.get('retiro_voluntario'),
                'cancelado': row.get('cancelado'),
                'cancelamiento_vit_comp': row.get('cancelamiento_vit_comp'),
                'desercion_vit_comp': row.get('desercion_vit_comp'),
                'por_certificar': row.get('por_certificar'),
                'certificados': row.get('certificados'),
                'traslados': row.get('traslados'),
                'otro': row.get('otro')
            }
            
            db.execute(update_datos_sql, data_dict)
            datos_actualizados += 1
        except SQLAlchemyError as e:
            msg = f"Error al actualizar datos del grupo {row['cod_ficha']} (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al actualizar datos de grupo: {e}")

    db.commit()
    return {
        "datos_actualizados": datos_actualizados,
        "errores": errores
    }

def upsert_competencia_bulk(db: Session, df_competencias: pd.DataFrame):
    """
    Inserta o actualiza competencias en la base de datos en lote.
    """
    competencias_insertadas = 0
    errores = []
    
    upsert_sql = text("""
        INSERT INTO competencia (cod_competencia, nombre, horas)
        VALUES (:cod_competencia, :nombre, :horas)
        ON DUPLICATE KEY UPDATE 
            nombre = VALUES(nombre),
            horas = VALUES(horas)
    """)
    
    for idx, row in df_competencias.iterrows():
        try:
            data_dict = {
                'cod_competencia': row.get('cod_competencia'),
                'nombre': row.get('nombre', '')[:500],  # Limitar longitud
                'horas': row.get('horas', 0)
            }
            
            db.execute(upsert_sql, data_dict)
            competencias_insertadas += 1
        except SQLAlchemyError as e:
            msg = f"Error al insertar competencia {row['cod_competencia']} (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar competencia: {e}")

    db.commit()
    return {
        "competencias_insertadas": competencias_insertadas,
        "errores": errores
    }

def upsert_resultado_aprendizaje_bulk(db: Session, df_resultados: pd.DataFrame):
    """
    Inserta o actualiza resultados de aprendizaje en la base de datos en lote.
    """
    resultados_insertados = 0
    errores = []
    
    upsert_sql = text("""
        INSERT INTO resultado_aprendizaje (cod_resultado, nombre, cod_competencia)
        VALUES (:cod_resultado, :nombre, :cod_competencia)
        ON DUPLICATE KEY UPDATE 
            nombre = VALUES(nombre),
            cod_competencia = VALUES(cod_competencia)
    """)
    
    for idx, row in df_resultados.iterrows():
        try:
            data_dict = {
                'cod_resultado': row.get('cod_resultado'),
                'nombre': row.get('nombre', '')[:500],  # Limitar longitud
                'cod_competencia': row.get('cod_competencia')
            }
            
            db.execute(upsert_sql, data_dict)
            resultados_insertados += 1
        except SQLAlchemyError as e:
            msg = f"Error al insertar resultado de aprendizaje {row['cod_resultado']} (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar resultado de aprendizaje: {e}")

    db.commit()
    return {
        "resultados_insertados": resultados_insertados,
        "errores": errores
    }

def upsert_programa_competencia_bulk(db: Session, df_programa_competencia: pd.DataFrame):
    """
    Inserta o actualiza relaciones programa-competencia en la base de datos en lote.
    """
    relaciones_insertadas = 0
    errores = []
    
    print(f"CRUD: Iniciando inserción de {len(df_programa_competencia)} relaciones programa-competencia")
    
    # Usar INSERT IGNORE para evitar duplicados, sin especificar cod_prog_competencia (AUTO_INCREMENT)
    upsert_sql = text("""
        INSERT IGNORE INTO programa_competencia (cod_programa, cod_competencia)
        VALUES (:cod_programa, :cod_competencia)
    """)
    
    for idx, row in df_programa_competencia.iterrows():
        try:
            data_dict = {
                'cod_programa': row.get('cod_programa'),
                'cod_competencia': row.get('cod_competencia')
            }
            
            print(f"CRUD: Insertando relación {idx+1}: programa={data_dict['cod_programa']}, competencia={data_dict['cod_competencia']}")
            
            result = db.execute(upsert_sql, data_dict)
            if result.rowcount > 0:  # Si se insertó una nueva fila
                relaciones_insertadas += 1
                print(f"CRUD: Relación insertada exitosamente (rowcount: {result.rowcount})")
            else:
                print(f"CRUD: Relación ya existía, no se insertó (rowcount: {result.rowcount})")
                
        except SQLAlchemyError as e:
            msg = f"Error al insertar programa-competencia programa:{row.get('cod_programa')} competencia:{row.get('cod_competencia')} (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar programa-competencia: {e}")
            print(f"CRUD: ERROR - {msg}")

    try:
        db.commit()
        print(f"CRUD: Commit exitoso. Total relaciones insertadas: {relaciones_insertadas}")
    except Exception as e:
        db.rollback()
        error_msg = f"Error en commit: {e}"
        errores.append(error_msg)
        print(f"CRUD: ERROR en commit - {error_msg}")
    
    return {
        "relaciones_insertadas": relaciones_insertadas,
        "errores": errores
    }
