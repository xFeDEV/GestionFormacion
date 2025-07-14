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
from app.schemas.grupos import RegionalCreate, CentroFormacionCreate
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
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce").dt.date

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