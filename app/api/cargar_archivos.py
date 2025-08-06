from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from io import BytesIO
from app.crud.cargar_archivos import (
    upsert_regional,
    upsert_centro_formacion,
    upsert_programas_formacion_bulk,
    upsert_grupos_bulk,
    upsert_datos_grupo_bulk
)
from app.schemas.grupos import RegionalCreate
from app.schemas.centro_formacion import CentroFormacionCreate
from core.database import get_db
import pandas as pd
import numpy as np

router = APIRouter()

@router.post("/upload-excel/")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    
    # Leer el archivo Excel con las nuevas columnas
    df = pd.read_excel(
        BytesIO(contents),
        engine="openpyxl",
        skiprows=4,
        usecols=[
            # Columnas existentes
            "IDENTIFICADOR_FICHA", "CODIGO_CENTRO", "CODIGO_PROGRAMA", "VERSION_PROGRAMA", 
            "NOMBRE_PROGRAMA_FORMACION", "ESTADO_CURSO", "NIVEL_FORMACION", "NOMBRE_JORNADA", 
            "FECHA_INICIO_FICHA", "FECHA_TERMINACION_FICHA", "ETAPA_FICHA", "MODALIDAD_FORMACION",
            "NOMBRE_RESPONSABLE", "NOMBRE_EMPRESA", "NOMBRE_MUNICIPIO_CURSO", "NOMBRE_PROGRAMA_ESPECIAL",
            # Nuevas columnas
            "CODIGO_REGIONAL", "NOMBRE_REGIONAL", "NOMBRE_CENTRO",
            "TOTAL_APRENDICES_MASCULINOS", "TOTAL_APRENDICES_FEMENINOS", "TOTAL_APRENDICES_NOBINARIO",
            "TOTAL_APRENDICES", "TOTAL_APRENDICES_ACTIVOS"
        ],
        dtype=str
    )
    
    print(f"Columnas cargadas: {df.columns.tolist()}")
    print(f"Filas cargadas: {len(df)}")

    # Renombrar columnas
    df = df.rename(columns={
        # Columnas existentes
        "IDENTIFICADOR_FICHA": "cod_ficha",
        "CODIGO_CENTRO": "cod_centro",
        "CODIGO_PROGRAMA": "cod_programa",
        "VERSION_PROGRAMA": "la_version",
        "ESTADO_CURSO": "estado_grupo",
        "NIVEL_FORMACION": "nombre_nivel",
        "NOMBRE_JORNADA": "jornada",
        "FECHA_INICIO_FICHA": "fecha_inicio",
        "FECHA_TERMINACION_FICHA": "fecha_fin",
        "ETAPA_FICHA": "etapa",
        "MODALIDAD_FORMACION": "modalidad",
        "NOMBRE_RESPONSABLE": "responsable",
        "NOMBRE_EMPRESA": "nombre_empresa",
        "NOMBRE_MUNICIPIO_CURSO": "nombre_municipio",
        "NOMBRE_PROGRAMA_ESPECIAL": "nombre_programa_especial",
        "NOMBRE_PROGRAMA_FORMACION": "nombre",
        # Nuevas columnas
        "CODIGO_REGIONAL": "cod_regional",
        "NOMBRE_REGIONAL": "nombre_regional",
        "NOMBRE_CENTRO": "nombre_centro",
        "TOTAL_APRENDICES_MASCULINOS": "num_aprendices_masculinos",
        "TOTAL_APRENDICES_FEMENINOS": "num_aprendices_femenino",
        "TOTAL_APRENDICES_NOBINARIO": "num_aprendices_no_binario",
        "TOTAL_APRENDICES": "num_total_aprendices",
        "TOTAL_APRENDICES_ACTIVOS": "num_total_aprendices_activos"
    })

    # Reemplazar valores NaN por None para compatibilidad con MySQL
    df = df.where(pd.notnull(df), None)

    # Convertir columnas numéricas
    numeric_columns = [
        "cod_ficha", "cod_centro", "cod_programa", "la_version", "cod_regional",
        "num_aprendices_masculinos", "num_aprendices_femenino", "num_aprendices_no_binario",
        "num_total_aprendices", "num_total_aprendices_activos"
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filtrar por cod_centro específico (opcional - comentar si se quiere cargar todos)
    # df = df[df["cod_centro"] == 9121]

    # Eliminar filas con valores faltantes en campos obligatorios
    required_fields = [
        "cod_ficha", "cod_centro", "cod_programa", "la_version", "nombre", 
        "fecha_inicio", "fecha_fin", "etapa", "responsable", "nombre_municipio"
    ]
    df = df.dropna(subset=required_fields)

    # Convertir fechas
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], format='%d/%m/%Y', errors="coerce").dt.date
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], format='%d/%m/%Y', errors="coerce").dt.date
    
    # Reemplazar valores NaT con None para compatibilidad con la base de datos
    df["fecha_inicio"] = df["fecha_inicio"].where(pd.notnull(df["fecha_inicio"]), None)
    df["fecha_fin"] = df["fecha_fin"].where(pd.notnull(df["fecha_fin"]), None)

    # Asegurar columnas de hora
    df["hora_inicio"] = "00:00:00"
    df["hora_fin"] = "00:00:00"

    print(f"Filas después de limpieza: {len(df)}")

    # Resultados de procesamiento
    resultados = {
        "regionales_procesadas": 0,
        "centros_procesados": 0,
        "programas_procesados": 0,
        "grupos_procesados": 0,
        "datos_grupo_procesados": 0,
        "errores": []
    }

    try:
        # 1. Procesar regionales (si existen datos)
        if "cod_regional" in df.columns and "nombre_regional" in df.columns:
            df_regionales = df[["cod_regional", "nombre_regional"]].dropna(subset=["cod_regional", "nombre_regional"]).drop_duplicates()
            df_regionales = df_regionales.rename({"nombre_regional": "nombre"}, axis=1)
            
            for _, row in df_regionales.iterrows():
                try:
                    regional = RegionalCreate(
                        cod_regional=int(row["cod_regional"]),
                        nombre=str(row["nombre"])
                    )
                    upsert_regional(db, regional)
                    resultados["regionales_procesadas"] += 1
                except Exception as e:
                    resultados["errores"].append(f"Error procesando regional {row['cod_regional']}: {e}")

        # 2. Procesar centros de formación (si existen datos)
        if all(col in df.columns for col in ["cod_centro", "nombre_centro", "cod_regional"]):
            df_centros = df[["cod_centro", "nombre_centro", "cod_regional"]].dropna(subset=["cod_centro", "nombre_centro", "cod_regional"]).drop_duplicates()
            
            for _, row in df_centros.iterrows():
                try:
                    centro = CentroFormacionCreate(
                        cod_centro=int(row["cod_centro"]),
                        nombre_centro=str(row["nombre_centro"]),
                        cod_regional=int(row["cod_regional"])
                    )
                    upsert_centro_formacion(db, centro)
                    resultados["centros_procesados"] += 1
                except Exception as e:
                    resultados["errores"].append(f"Error procesando centro {row['cod_centro']}: {e}")

        # 3. Procesar programas de formación
        df_programas = df[["cod_programa", "la_version", "nombre"]].dropna(subset=["cod_programa", "la_version", "nombre"]).drop_duplicates()
        df_programas["horas_lectivas"] = 0
        df_programas["horas_productivas"] = 0
        
        programas_result = upsert_programas_formacion_bulk(db, df_programas)
        resultados["programas_procesados"] = programas_result["programas_insertados"]
        resultados["errores"].extend(programas_result["errores"])

        # 4. Procesar grupos
        df_grupos = df[[
            "cod_ficha", "cod_centro", "cod_programa", "la_version", "estado_grupo",
            "nombre_nivel", "jornada", "fecha_inicio", "fecha_fin", "etapa",
            "modalidad", "responsable", "nombre_empresa", "nombre_municipio",
            "nombre_programa_especial", "hora_inicio", "hora_fin"
        ]].dropna(subset=["cod_ficha"])
        
        grupos_result = upsert_grupos_bulk(db, df_grupos)
        resultados["grupos_procesados"] = grupos_result["grupos_insertados"]
        resultados["errores"].extend(grupos_result["errores"])

        # 5. Procesar datos de grupo (si existen datos)
        datos_grupo_columns = [
            "cod_ficha", "num_aprendices_masculinos", "num_aprendices_femenino",
            "num_aprendices_no_binario", "num_total_aprendices", "num_total_aprendices_activos"
        ]
        
        # Filtrar solo las columnas que existen en el DataFrame
        existing_columns = [col for col in datos_grupo_columns if col in df.columns]
        
        if "cod_ficha" in existing_columns and len(existing_columns) > 1:
            df_datos_grupo = df[existing_columns].dropna(subset=["cod_ficha"])
            
            # Filtrar filas que tienen al menos un dato de aprendices
            numeric_cols = [col for col in existing_columns if col != "cod_ficha"]
            df_datos_grupo = df_datos_grupo.dropna(subset=numeric_cols, how="all")
            
            if len(df_datos_grupo) > 0:
                datos_result = upsert_datos_grupo_bulk(db, df_datos_grupo)
                resultados["datos_grupo_procesados"] = datos_result["datos_insertados"]
                resultados["errores"].extend(datos_result["errores"])

        # Mensaje final
        resultados["mensaje"] = "Carga completada con errores" if resultados["errores"] else "Carga completada exitosamente"
        
        return resultados

    except Exception as e:
        resultados["errores"].append(f"Error general en el procesamiento: {str(e)}")
        resultados["mensaje"] = "Error crítico en el procesamiento"
        return resultados

@router.post("/upload-df14-excel/", tags=["Cargar Archivos"])
async def upload_df14_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint para procesar el archivo DF-14 que contiene información de duraciones
    de programas y estados detallados de aprendices.
    """
    from app.crud.cargar_archivos import update_programas_duracion_bulk, update_datos_grupo_bulk
    
    contents = await file.read()
    
    # Leer el archivo Excel DF-14
    df = pd.read_excel(
        BytesIO(contents),
        engine="openpyxl",
        skiprows=4,  # Ajustar según sea necesario
        usecols=[
            # Llaves identificadoras
            "FICHA", "CODIGO_PROGRAMA", "VERSION_PROGRAMA",
            # Duraciones de programas
            "DURACION_ETAPA_LECTIVA", "DURACION_ETAPA_PRODUCTIVA",
            # Datos de cupo y estados de aprendices
            "CUPO", "EN_TRANSITO", "INDUCCION", "FORMACION", "CONDICIONADO",
            "APLAZADO", "RETIRO_VOLUNTARIO", "CANCELAMIENTO_VIRT_COMP",
            "DESERCION_VIRT_COMP", "CANCELADO", "POR_CERTIFICAR",
            "CERTIFICADO", "TRASLADADO", "OTRO"
        ],
        dtype=str
    )
    
    print(f"Archivo DF-14 - Columnas cargadas: {df.columns.tolist()}")
    print(f"Archivo DF-14 - Filas cargadas: {len(df)}")

    # Renombrar columnas para que coincidan con la base de datos
    df = df.rename(columns={
        # Llaves identificadoras
        "FICHA": "cod_ficha",
        "CODIGO_PROGRAMA": "cod_programa",
        "VERSION_PROGRAMA": "la_version",
        # Duraciones de programas
        "DURACION_ETAPA_LECTIVA": "horas_lectivas",
        "DURACION_ETAPA_PRODUCTIVA": "horas_productivas",
        # Datos de cupo y estados de aprendices
        "CUPO": "cupo_total",
        "EN_TRANSITO": "en_transito",
        "INDUCCION": "induccion",
        "FORMACION": "formacion",
        "CONDICIONADO": "condicionado",
        "APLAZADO": "aplazado",
        "RETIRO_VOLUNTARIO": "retiro_voluntario",
        "CANCELAMIENTO_VIRT_COMP": "cancelamiento_vit_comp",
        "DESERCION_VIRT_COMP": "desercion_vit_comp",
        "CANCELADO": "cancelado",
        "POR_CERTIFICAR": "por_certificar",
        "CERTIFICADO": "certificados",
        "TRASLADADO": "traslados",
        "OTRO": "otro"
    })

    # Reemplazar valores NaN por None para compatibilidad con MySQL
    df = df.where(pd.notnull(df), None)

    # Convertir columnas a tipos numéricos
    numeric_columns = [
        "cod_ficha", "cod_programa", "la_version", "horas_lectivas", "horas_productivas",
        "cupo_total", "en_transito", "induccion", "formacion", "condicionado",
        "aplazado", "retiro_voluntario", "cancelamiento_vit_comp", "desercion_vit_comp",
        "cancelado", "por_certificar", "certificados", "traslados", "otro"
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Eliminar filas con valores faltantes en campos obligatorios
    df = df.dropna(subset=["cod_ficha", "cod_programa", "la_version"])

    print(f"Archivo DF-14 - Filas después de limpieza: {len(df)}")

    # Resultados de procesamiento
    resultados = {
        "programas_actualizados": 0,
        "datos_grupo_actualizados": 0,
        "errores": []
    }

    try:
        # 1. Actualizar duraciones de programas
        if all(col in df.columns for col in ["cod_programa", "la_version", "horas_lectivas", "horas_productivas"]):
            df_programas = df[["cod_programa", "la_version", "horas_lectivas", "horas_productivas"]]
            df_programas = df_programas.dropna(subset=["cod_programa", "la_version"])
            df_programas = df_programas.drop_duplicates(subset=["cod_programa", "la_version"])
            
            if len(df_programas) > 0:
                programas_result = update_programas_duracion_bulk(db, df_programas)
                resultados["programas_actualizados"] = programas_result["programas_actualizados"]
                resultados["errores"].extend(programas_result["errores"])

        # 2. Actualizar datos de grupo
        datos_grupo_columns = [
            "cod_ficha", "cupo_total", "en_transito", "induccion", "formacion",
            "condicionado", "aplazado", "retiro_voluntario", "cancelamiento_vit_comp",
            "desercion_vit_comp", "cancelado", "por_certificar", "certificados",
            "traslados", "otro"
        ]
        
        # Filtrar solo las columnas que existen en el DataFrame
        existing_columns = [col for col in datos_grupo_columns if col in df.columns]
        
        if "cod_ficha" in existing_columns and len(existing_columns) > 1:
            df_datos_grupo = df[existing_columns]
            df_datos_grupo = df_datos_grupo.dropna(subset=["cod_ficha"])
            
            # Filtrar filas que tienen al menos un dato de estado
            estado_cols = [col for col in existing_columns if col != "cod_ficha"]
            df_datos_grupo = df_datos_grupo.dropna(subset=estado_cols, how="all")
            
            if len(df_datos_grupo) > 0:
                datos_result = update_datos_grupo_bulk(db, df_datos_grupo)
                resultados["datos_grupo_actualizados"] = datos_result["datos_actualizados"]
                resultados["errores"].extend(datos_result["errores"])

        # Mensaje final
        resultados["mensaje"] = "Archivo DF-14 procesado y datos actualizados correctamente"
        if resultados["errores"]:
            resultados["mensaje"] += " (con algunos errores)"
        
        return resultados

    except Exception as e:
        resultados["errores"].append(f"Error general procesando DF-14: {str(e)}")
        resultados["mensaje"] = "Error crítico procesando archivo DF-14"
        return resultados

@router.post("/upload-evaluaciones-excel/", tags=["Cargar Archivos"])
async def upload_evaluaciones_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint para procesar el archivo de evaluaciones que contiene:
    - Tabla 1: Ficha de caracterización (A2-A12)
    - Tabla 2: Datos de evaluaciones con competencias y resultados de aprendizaje
    """
    from app.crud.cargar_archivos import upsert_competencia_bulk, upsert_resultado_aprendizaje_bulk, upsert_programa_competencia_bulk
    
    contents = await file.read()
    
    try:
        # Leer la primera tabla (A2-A12) para obtener la ficha de caracterización
        # La ficha está específicamente en la celda C3
        df_ficha = pd.read_excel(
            BytesIO(contents),
            engine="openpyxl",
            usecols="A:C",  # Columnas A, B y C
            skiprows=1,     # Saltar las primeras 2 filas para llegar a la fila 3
            nrows=1         # Leer solo 1 fila (fila 3)
        )
        
        # Extraer la ficha de caracterización de la celda C3
        ficha_caracterizacion = None
        if len(df_ficha.columns) >= 3 and len(df_ficha) > 0:
            ficha_value = df_ficha.iloc[0, 2]  # Tercera columna (C), primera fila
            if pd.notna(ficha_value):
                ficha_caracterizacion = str(ficha_value).strip()
                # Limpiar y convertir a número si es posible
                try:
                    # Remover espacios y caracteres no numéricos excepto puntos y comas
                    cleaned_value = ''.join(c for c in ficha_caracterizacion if c.isdigit() or c in '.,')
                    if cleaned_value:
                        ficha_caracterizacion = str(int(float(cleaned_value.replace(',', ''))))
                except Exception as convert_error:
                    print(f"No se pudo convertir la ficha a número: {convert_error}")
                    # Mantener el valor original como string
                    pass
        
        print(f"Ficha de caracterización encontrada en C3: {ficha_caracterizacion}")
        
        # Leer la segunda tabla con los datos de evaluaciones
        # Buscar donde comienza la tabla de evaluaciones (después de A12)
        df_evaluaciones = pd.read_excel(
            BytesIO(contents),
            engine="openpyxl",
            skiprows=13  # Comenzar después de A12, ajustar según sea necesario
        )
        
        # Renombrar columnas para facilitar el procesamiento
        expected_columns = [
            "tipo_documento", "numero_documento", "nombre", "apellidos", "estado",
            "competencia", "resultado_aprendizaje", "juicio_evaluacion", 
            "fecha_hora_juicio", "funcionario_registro"
        ]
        
        # Asignar nombres a las columnas si coinciden en número
        if len(df_evaluaciones.columns) >= len(expected_columns):
            df_evaluaciones.columns = expected_columns + list(df_evaluaciones.columns[len(expected_columns):])
        
        print(f"Columnas de evaluaciones: {df_evaluaciones.columns.tolist()}")
        print(f"Filas de evaluaciones cargadas: {len(df_evaluaciones)}")
        
        # Agregar la ficha de caracterización como nueva columna
        df_evaluaciones["cod_ficha"] = ficha_caracterizacion
        
        # Limpiar datos
        df_evaluaciones = df_evaluaciones.where(pd.notnull(df_evaluaciones), None)
        df_evaluaciones = df_evaluaciones.dropna(subset=["competencia", "resultado_aprendizaje"])
        
        print(f"Filas después de limpieza: {len(df_evaluaciones)}")
        
        # Función para extraer código y nombre de una cadena
        def extraer_codigo_nombre(texto):
            if pd.isna(texto) or not isinstance(texto, str):
                return None, None
            
            # Buscar patrón: número al inicio seguido de " - "
            import re
            match = re.match(r'^(\d+)\s*-\s*(.+)$', texto.strip())
            if match:
                codigo = int(match.group(1))
                nombre = match.group(2).strip()
                return codigo, nombre
            return None, texto.strip()
        
        # Procesar competencias
        competencias_data = []
        competencias_vistas = set()
        
        for _, row in df_evaluaciones.iterrows():
            if pd.notna(row["competencia"]):
                cod_competencia, nombre_competencia = extraer_codigo_nombre(row["competencia"])
                
                if cod_competencia and cod_competencia not in competencias_vistas:
                    # Extraer horas de la fecha_hora_juicio (si está disponible)
                    horas = 0
                    if pd.notna(row["fecha_hora_juicio"]):
                        # Intentar extraer horas del campo si es un string con formato específico
                        try:
                            if isinstance(row["fecha_hora_juicio"], str):
                                # Si hay un patrón específico para las horas, ajustar aquí
                                horas = 0  # Por defecto
                        except:
                            horas = 0
                    
                    competencias_data.append({
                        "cod_competencia": int(cod_competencia),
                        "nombre": str(nombre_competencia) if nombre_competencia else "",
                        "horas": int(horas) if pd.notna(horas) and horas is not None else 0
                    })
                    competencias_vistas.add(cod_competencia)
        
        # Procesar resultados de aprendizaje
        resultados_data = []
        resultados_vistos = set()
        
        for _, row in df_evaluaciones.iterrows():
            if pd.notna(row["resultado_aprendizaje"]) and pd.notna(row["competencia"]):
                cod_resultado, nombre_resultado = extraer_codigo_nombre(row["resultado_aprendizaje"])
                cod_competencia, _ = extraer_codigo_nombre(row["competencia"])
                
                if cod_resultado and cod_competencia and cod_resultado not in resultados_vistos:
                    resultados_data.append({
                        "cod_resultado": int(cod_resultado),
                        "nombre": str(nombre_resultado) if nombre_resultado else "",
                        "cod_competencia": int(cod_competencia)
                    })
                    resultados_vistos.add(cod_resultado)
        
        # Convertir a DataFrames
        df_competencias = pd.DataFrame(competencias_data)
        df_resultados = pd.DataFrame(resultados_data)
        
        print(f"Competencias extraídas: {len(df_competencias)}")
        print(f"Resultados de aprendizaje extraídos: {len(df_resultados)}")
        
        # Obtener cod_programa de la ficha de caracterización
        cod_programa = None
        debug_cod_programa = {}
        
        if ficha_caracterizacion:
            try:
                # Buscar directamente el cod_programa en la tabla grupos donde cod_programa = ficha
                from sqlalchemy import text
                
                query_programa = text("""
                    SELECT cod_programa 
                    FROM grupo 
                    WHERE cod_programa = :ficha_code 
                    LIMIT 1
                """)
                result = db.execute(query_programa, {"ficha_code": ficha_caracterizacion}).fetchone()
                
                if result:
                    cod_programa = result[0]
                    debug_cod_programa = {
                        "ficha_buscada": ficha_caracterizacion,
                        "cod_programa_encontrado": cod_programa,
                        "query_ejecutada": "SELECT cod_programa FROM grupo WHERE cod_programa = ficha",
                        "tipo_busqueda": "string"
                    }
                    print(f"Código de programa encontrado (como string): {cod_programa}")
                else:
                    # Intentar buscar con conversión a entero
                    try:
                        ficha_as_int = int(ficha_caracterizacion)
                        result_int = db.execute(query_programa, {"ficha_code": ficha_as_int}).fetchone()
                        if result_int:
                            cod_programa = result_int[0]
                            debug_cod_programa = {
                                "ficha_buscada": ficha_caracterizacion,
                                "ficha_como_int": ficha_as_int,
                                "cod_programa_encontrado": cod_programa,
                                "query_ejecutada": "SELECT cod_programa FROM grupo WHERE cod_programa = ficha",
                                "tipo_busqueda": "int"
                            }
                            print(f"Código de programa encontrado (como int): {cod_programa}")
                        else:
                            debug_cod_programa = {
                                "ficha_buscada": ficha_caracterizacion,
                                "ficha_como_int": ficha_as_int,
                                "cod_programa_encontrado": None,
                                "query_ejecutada": "SELECT cod_programa FROM grupo WHERE cod_programa = ficha",
                                "tipo_busqueda": "ambos_fallaron"
                            }
                            print(f"No se encontró código de programa para la ficha: {ficha_caracterizacion}")
                    except ValueError as ve:
                        debug_cod_programa = {
                            "ficha_buscada": ficha_caracterizacion,
                            "error_conversion": str(ve),
                            "query_ejecutada": "SELECT cod_programa FROM grupo WHERE cod_programa = ficha",
                            "tipo_busqueda": "solo_string_fallido"
                        }
                        print(f"Error convirtiendo ficha a int: {ve}")
                        print(f"No se encontró código de programa para la ficha (como string): {ficha_caracterizacion}")
                
                # Si aún no encontramos nada, hacer más debugging
                if not cod_programa:
                    print("DEBUGGING: Buscando información adicional...")
                    
                    # Verificar si la ficha existe en grupo
                    check_grupos_query = text("""
                        SELECT cod_ficha, cod_programa FROM grupo WHERE cod_ficha = :ficha_code
                    """)
                    grupos_result = db.execute(check_grupos_query, {"ficha_code": ficha_caracterizacion}).fetchone()
                    if grupos_result:
                        print(f"Ficha encontrada en grupo: cod_ficha={grupos_result[0]}, cod_programa={grupos_result[1]}")
                        
                        # Verificar si el programa existe en programa_formacion
                        check_programa_query = text("""
                            SELECT cod_programa FROM programa_formacion WHERE cod_programa = :cod_programa
                        """)
                        programa_result = db.execute(check_programa_query, {"cod_programa": grupos_result[1]}).fetchone()
                        if programa_result:
                            print(f"Programa encontrado en programa_formacion: {programa_result[0]}")
                            cod_programa = programa_result[0]
                        else:
                            print(f"PROBLEMA: Programa {grupos_result[1]} NO existe en tabla programa_formacion")
                    else:
                        print(f"Ficha {ficha_caracterizacion} NO encontrada en tabla grupo")
                    
                    # Buscar fichas similares
                    search_query = text("""
                        SELECT g.cod_ficha, g.cod_programa FROM grupo g 
                        WHERE g.cod_ficha LIKE :pattern 
                        ORDER BY g.cod_ficha LIMIT 10
                    """)
                    similar_results = db.execute(search_query, {"pattern": f"%{ficha_caracterizacion[-4:]}%"}).fetchall()
                    print(f"Fichas similares encontradas: {[(r[0], r[1]) for r in similar_results]}")
                    
                    # Contar total de grupos
                    count_query = text("SELECT COUNT(*) FROM grupo WHERE cod_ficha IS NOT NULL")
                    count_result = db.execute(count_query).fetchone()
                    print(f"Total de grupos con cod_ficha en la base de datos: {count_result[0] if count_result else 0}")
                    
                    # Mostrar ejemplos de fichas
                    sample_query = text("SELECT cod_ficha, cod_programa FROM grupo WHERE cod_ficha IS NOT NULL LIMIT 10")
                    sample_results = db.execute(sample_query).fetchall()
                    print(f"Ejemplos de fichas en la base de datos: {[(r[0], r[1]) for r in sample_results]}")
                    
            except Exception as e:
                debug_cod_programa = {
                    "ficha_buscada": ficha_caracterizacion,
                    "error_excepcion": str(e),
                    "query_ejecutada": "SELECT cod_programa FROM grupo WHERE cod_programa = ficha",
                    "tipo_busqueda": "error_excepcion"
                }
                print(f"Error al buscar código de programa: {e}")
                import traceback
                print(f"Traceback completo: {traceback.format_exc()}")
        else:
            debug_cod_programa = {
                "ficha_buscada": None,
                "error": "No se pudo obtener ficha_caracterizacion",
                "query_ejecutada": "ninguna",
                "tipo_busqueda": "sin_ficha"
            }
            print("No se pudo obtener ficha_caracterizacion para buscar cod_programa")
        
        # Crear relaciones programa-competencia
        programa_competencia_data = []
        if cod_programa and len(df_competencias) > 0:
            print(f"Creando relaciones programa-competencia para programa {cod_programa} con {len(df_competencias)} competencias")
            for idx, row in df_competencias.iterrows():
                programa_competencia_data.append({
                    # No incluir cod_prog_competencia ya que es AUTO_INCREMENT
                    "cod_competencia": row['cod_competencia'],
                    "cod_programa": cod_programa
                })
        else:
            if not cod_programa:
                print("No se puede crear relaciones programa-competencia: cod_programa no encontrado")
            if len(df_competencias) == 0:
                print("No se puede crear relaciones programa-competencia: no hay competencias extraídas")
        
        df_programa_competencia = pd.DataFrame(programa_competencia_data)
        print(f"Relaciones programa-competencia creadas: {len(df_programa_competencia)}")
        
        # Resultados de procesamiento
        resultados = {
            "ficha_caracterizacion": ficha_caracterizacion,
            "competencias_procesadas": 0,
            "resultados_procesados": 0,
            "programa_competencia_procesadas": 0,
            "registros_evaluaciones": int(len(df_evaluaciones)),
            "errores": [],
            # Campos de debug temporales
            "debug_cod_programa_info": debug_cod_programa,
            "debug_competencias_count": len(df_competencias),
            "debug_programa_competencia_data_count": len(df_programa_competencia)
        }
        
        # Guardar competencias en la base de datos
        if len(df_competencias) > 0:
            competencias_result = upsert_competencia_bulk(db, df_competencias)
            resultados["competencias_procesadas"] = int(competencias_result.get("competencias_insertadas", 0))
            resultados["errores"].extend(competencias_result.get("errores", []))
        
        # Guardar resultados de aprendizaje en la base de datos
        if len(df_resultados) > 0:
            resultados_result = upsert_resultado_aprendizaje_bulk(db, df_resultados)
            resultados["resultados_procesados"] = int(resultados_result.get("resultados_insertados", 0))
            resultados["errores"].extend(resultados_result.get("errores", []))
        
        # Guardar relaciones programa-competencia en la base de datos
        if len(df_programa_competencia) > 0:
            try:
                programa_comp_result = upsert_programa_competencia_bulk(db, df_programa_competencia)
                resultados["programa_competencia_procesadas"] = int(programa_comp_result.get("relaciones_insertadas", 0))
                resultados["errores"].extend(programa_comp_result.get("errores", []))
                resultados["debug_programa_comp_result"] = programa_comp_result
            except Exception as e:
                error_msg = f"Error al procesar programa_competencia: {str(e)}"
                resultados["errores"].append(error_msg)
                resultados["debug_programa_comp_error"] = error_msg
        else:
            resultados["debug_programa_comp_message"] = "No hay relaciones programa-competencia para procesar"
        
        # Mensaje final
        resultados["mensaje"] = "Archivo de evaluaciones procesado correctamente"
        if resultados["errores"]:
            resultados["mensaje"] += " (con algunos errores)"
        
        return resultados
        
    except Exception as e:
        return {
            "mensaje": "Error crítico procesando archivo de evaluaciones",
            "errores": [f"Error general: {str(e)}"],
            "ficha_caracterizacion": None,
            "competencias_procesadas": 0,
            "resultados_procesados": 0,
            "programa_competencia_procesadas": 0,
            "registros_evaluaciones": 0,
            "debug_cod_programa_info": {},
            "debug_competencias_count": 0,
            "debug_programa_competencia_data_count": 0
        }