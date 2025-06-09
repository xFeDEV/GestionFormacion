from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def insertar_datos_en_bd(db: Session, df_programas, df):
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
            if result.rowcount == 1:
                programas_insertados += 1
            elif result.rowcount == 2:
                programas_actualizados += 1
        except SQLAlchemyError as e:
            msg = f"Error al insertar programa (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar: {e}")

    # # 2. Insertar grupos
    insert_grupo_sql = text("""
        INSERT INTO grupo (
            cod_ficha, cod_centro, cod_programa, la_version, estado_grupo,
            nombre_nivel, jornada, fecha_inicio, fecha_fin, etapa,
            modalidad, responsable, nombre_empresa, nombre_municipio,
            nombre_programa_especial, hora_inicio, hora_fin, aula_actual
        ) VALUES (
            :cod_ficha, :cod_centro, :cod_programa, :la_version, :estado_grupo,
            :nombre_nivel, :jornada, :fecha_inicio, :fecha_fin, :etapa,
            :modalidad, :responsable, :nombre_empresa, :nombre_municipio,
            :nombre_programa_especial, :hora_inicio, :hora_fin, :aula_actual
        )
        ON DUPLICATE KEY UPDATE
            estado_grupo=VALUES(estado_grupo),
            etapa=VALUES(etapa),
            responsable=VALUES(responsable),
            nombre_programa_especial=VALUES(nombre_programa_especial),
            hora_inicio=VALUES(hora_inicio),
            hora_fin=VALUES(hora_fin),
            aula_actual=VALUES(aula_actual)
    """)

    for idx, row in df.iterrows():
        try:
            result = db.execute(insert_grupo_sql, row.to_dict())
            # En MySQL, ON DUPLICATE KEY UPDATE hace que rowcount sea 1 para insert y 2 para update
            if result.rowcount == 1:
                grupos_insertados += 1
            elif result.rowcount == 2:
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
