from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from io import BytesIO
from app.crud.cargar_archivos import insertar_datos_en_bd
from core.database import get_db
import pandas as pd

router = APIRouter()

@router.post("/upload-excel/")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    df = pd.read_excel(
        BytesIO(contents),
        engine="openpyxl",
        skiprows=4,
        usecols=["IDENTIFICADOR_FICHA", "CODIGO_CENTRO", "CODIGO_PROGRAMA", "VERSION_PROGRAMA", "NOMBRE_PROGRAMA_FORMACION",
                 "ESTADO_CURSO", "NIVEL_FORMACION", "NOMBRE_JORNADA", "FECHA_INICIO_FICHA", "FECHA_TERMINACION_FICHA",  "ETAPA_FICHA", "MODALIDAD_FORMACION",
                 "NOMBRE_RESPONSABLE", "NOMBRE_EMPRESA", "NOMBRE_MUNICIPIO_CURSO", "NOMBRE_PROGRAMA_ESPECIAL", 
                 ],  # Nombres reales
        dtype=str
    )
    print(df.head())  # paréntesis
    print(df.columns)
    print(df.dtypes)

    # Renombrar columnas
    df = df.rename(columns={
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
        "NOMBRE_PROGRAMA_FORMACION": "nombre"
    })


    print(df.head())  # paréntesis

    # Filtrar por cod_centro específico borrar si quiere ingresar todos los centros
    df =df[df["cod_centro"] == '9121']

    print(df.head())  # paréntesis

    # # Eliminar filas con valores faltantes en campos obligatorios
    required_fields = [
         "cod_ficha", "cod_centro", "cod_programa", "la_version", "nombre", "fecha_inicio", 
         "fecha_fin", "etapa", "responsable", "nombre_municipio"
    ]
    df = df.dropna(subset=required_fields)

    # Convertir columnas a tipo numérico
    for col in ["cod_ficha", "cod_programa", "la_version", "cod_centro"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    
    print(df.head())  # paréntesis

    print(df.dtypes)

    # # Convertir fechas
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce").dt.date

    # # Asegurar columnas no proporcionadas
    df["hora_inicio"] = "00:00:00"
    df["hora_fin"] = "00:00:00"

    # Crear DataFrame de programas únicos
    df_programas = df[["cod_programa", "la_version", "nombre"]].drop_duplicates()
    df_programas["horas_lectivas"] = 0
    df_programas["horas_productivas"] = 0

    print(df_programas.head())
    print(df.head())

    resultados = insertar_datos_en_bd(db, df_programas, df)
    return resultados