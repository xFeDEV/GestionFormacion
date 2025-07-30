from ast import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.grupos import GrupoUpdate, GrupoOut, GrupoSelect, DashboardKPISchema, GruposPorMunicipioSchema, GruposPorJornadaSchema, GruposPorModalidadSchema, GruposPorEtapaSchema, GruposPorNivelSchema
from app.crud import grupos as crud_grupo
from core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut
from typing import List, Optional

router = APIRouter()

# Rutas específicas primero para evitar conflictos con rutas paramétricas

@router.get("/search", response_model=List[GrupoSelect])
def search_grupos_for_select(
    search: str = Query("", description="Texto para buscar en código de ficha o nombre de programa"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de resultados"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Busca grupos para usar en un select/autocompletar.
    Permite buscar por código de ficha o nombre del programa.
    Útil para formularios donde se necesita seleccionar un grupo.
    """
    try:
        grupos = crud_grupo.search_grupos_for_select(db, search_text=search, limit=limit)
        return grupos
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/centro/{cod_centro}", response_model=List[GrupoOut])
def get_grupos_by_centro(
    cod_centro: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene una lista de todos los grupos que pertenecen a un centro de formación.
    """
    grupos_db = crud_grupo.get_grupos_by_cod_centro(db, cod_centro=cod_centro)
    # Si no se encuentran grupos, devuelve una lista vacía, lo cual es correcto.
    return grupos_db


@router.get("/kpis", response_model=DashboardKPISchema)
def get_dashboard_kpis(
    cod_centro: int = Query(..., description="Código del centro de formación (Obligatorio)"),
    estado_grupo: str = Query(..., description="Estado del grupo (Obligatorio)"),
    año: Optional[int] = Query(None, description="Filtrar por año de inicio (Opcional)"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene el número total de grupos según los filtros aplicados.
    """
    try:
        kpis = crud_grupo.get_dashboard_kpis(db, cod_centro=cod_centro, estado_grupo=estado_grupo, año=año)
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Endpoints de Distribución con Filtros ---

@router.get("/distribucion/por-municipio", response_model=List[GruposPorMunicipioSchema])
def get_distribucion_por_municipio(
    cod_centro: int = Query(..., description="Código del centro de formación (Obligatorio)"),
    estado_grupo: str = Query(..., description="Estado del grupo (Obligatorio)"),
    año: Optional[int] = Query(None, description="Filtrar por año de inicio (Opcional)"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene la distribución de grupos por municipio con filtros.
    """
    try:
        return crud_grupo.get_grupos_por_municipio_filtrado(db, cod_centro, estado_grupo, año)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribucion/por-jornada", response_model=List[GruposPorJornadaSchema])
def get_distribucion_por_jornada(
    cod_centro: int = Query(..., description="Código del centro de formación (Obligatorio)"),
    estado_grupo: str = Query(..., description="Estado del grupo (Obligatorio)"),
    año: Optional[int] = Query(None, description="Filtrar por año de inicio (Opcional)"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene la distribución de grupos por jornada con filtros.
    """
    try:
        return crud_grupo.get_grupos_por_jornada_filtrado(db, cod_centro, estado_grupo, año)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribucion/por-modalidad", response_model=List[GruposPorModalidadSchema])
def get_distribucion_por_modalidad(
    cod_centro: int = Query(..., description="Código del centro de formación (Obligatorio)"),
    estado_grupo: str = Query(..., description="Estado del grupo (Obligatorio)"),
    año: Optional[int] = Query(None, description="Filtrar por año de inicio (Opcional)"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene la distribución de grupos por modalidad con filtros.
    """
    try:
        return crud_grupo.get_grupos_por_modalidad_filtrado(db, cod_centro, estado_grupo, año)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribucion/por-etapa", response_model=List[GruposPorEtapaSchema])
def get_distribucion_por_etapa(
    cod_centro: int = Query(..., description="Código del centro de formación (Obligatorio)"),
    estado_grupo: str = Query(..., description="Estado del grupo (Obligatorio)"),
    año: Optional[int] = Query(None, description="Filtrar por año de inicio (Opcional)"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene la distribución de grupos por etapa con filtros.
    """
    try:
        return crud_grupo.get_grupos_por_etapa_filtrado(db, cod_centro, estado_grupo, año)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribucion/por-nivel", response_model=List[GruposPorNivelSchema])
def get_distribucion_por_nivel(
    cod_centro: int = Query(..., description="Código del centro de formación (Obligatorio)"),
    estado_grupo: str = Query(..., description="Estado del grupo (Obligatorio)"),
    año: Optional[int] = Query(None, description="Filtrar por año de inicio (Opcional)"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene la distribución de grupos por nivel de formación con filtros.
    """
    try:
        return crud_grupo.get_grupos_por_nivel_filtrado(db, cod_centro, estado_grupo, año)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Rutas paramétricas al final

@router.get("/{cod_ficha}", response_model=GrupoOut)
def get_grupo(
    cod_ficha: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene un grupo específico por su cod_ficha.
    Maneja correctamente los valores nulos y los horarios en 00:00:00.
    """
    try:
        grupo = crud_grupo.get_grupo_by_cod_ficha(db, cod_ficha=cod_ficha)
        if grupo is None:
            raise HTTPException(status_code=404, detail="Grupo no encontrado")
        return grupo
    except Exception as e:
        # Evita reenviar el detalle de una excepción HTTP ya lanzada
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{cod_ficha}")
def update_grupo(
    cod_ficha: int,
    grupo: GrupoUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Actualiza la hora de inicio, hora de fin y el aula actual de un grupo específico.
    """
    # Solo superadmin (1) y admin (2) pueden actualizar
    if current_user.id_rol not in [1, 2]:
        raise HTTPException(status_code=401, detail="No autorizado para realizar esta acción")

    try:
        success = crud_grupo.update_grupo(db, cod_ficha, grupo)
        if not success:
            raise HTTPException(status_code=404, detail="Grupo no encontrado o sin cambios para aplicar")
        return {"message": "Grupo actualizado correctamente"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


