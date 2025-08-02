from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.programacion import (ProgramacionCreate, ProgramacionUpdate, ProgramacionOut, 
                                    CompetenciaOut, ResultadoAprendizajeOut, ValidarCruceRequest, ValidarCruceResponse)
from app.crud import programacion as crud_programacion
from core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.users import UserOut
from typing import List

router = APIRouter()

@router.post("/validar-cruce", response_model=ValidarCruceResponse)
def validar_cruce_programacion(
    request: ValidarCruceRequest,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Valida si existe un cruce de horarios para una programación.
    
    Verifica si el instructor ya tiene una programación que se solape 
    en la fecha y horario especificados.
    """
    if current_user.id_rol not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado para realizar esta acción")
    
    try:
        # Construir consulta base
        verificacion_query_base = """
            SELECT COUNT(*) as conflictos
            FROM programacion 
            WHERE id_instructor = :id_instructor 
              AND fecha_programada = :fecha_programada
              AND ((:hora_inicio < hora_fin) AND (:hora_fin > hora_inicio))
        """
        
        # Parámetros base
        verificacion_params = {
            "id_instructor": request.id_instructor,
            "fecha_programada": request.fecha_programada,
            "hora_inicio": request.hora_inicio,
            "hora_fin": request.hora_fin
        }
        
        # Si se proporciona id_programacion_actual, excluirlo de la verificación
        if request.id_programacion_actual is not None:
            verificacion_query_base += " AND id_programacion != :id_programacion_actual"
            verificacion_params["id_programacion_actual"] = request.id_programacion_actual
        
        verificacion_query = text(verificacion_query_base)
        resultado_verificacion = db.execute(verificacion_query, verificacion_params).mappings().first()
        
        conflicto = resultado_verificacion and resultado_verificacion['conflictos'] > 0
        
        return ValidarCruceResponse(
            conflicto=conflicto,
            mensaje="El instructor ya tiene una programación que se cruza en este horario" if conflicto else "No hay conflictos de horario"
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al validar cruce de programación: {str(e)}")

# Endpoints específicos primero para evitar conflictos con rutas paramétricas
@router.get("/competencias/{cod_programa}/{la_version}", response_model=List[CompetenciaOut])
def get_competencias_by_programa(
    cod_programa: int,
    la_version: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todas las competencias asociadas a un programa de formación específico.
    
    Nota: Las competencias están asociadas al programa en general, no a una versión específica,
    por lo que el parámetro la_version se mantiene por compatibilidad pero no afecta el resultado.
    """
    try:
        competencias = crud_programacion.get_competencias_by_programa(db, cod_programa=cod_programa, la_version=la_version)
        return competencias
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resultados/{cod_competencia}", response_model=List[ResultadoAprendizajeOut])
def get_resultados_by_competencia(
    cod_competencia: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todos los resultados de aprendizaje para una competencia específica.
    """
    try:
        resultados = crud_programacion.get_resultados_by_competencia(db, cod_competencia=cod_competencia)
        return resultados
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instructor/{id_instructor}", response_model=List[ProgramacionOut])
def get_programaciones_by_instructor(
    id_instructor: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todas las programaciones de un instructor específico.
    Los instructores solo pueden ver sus propias programaciones, 
    mientras que admin y superadmin pueden ver las de cualquier instructor.
    """
    # Los instructores solo pueden ver sus propias programaciones
    if current_user.id_rol == 3 and current_user.id_usuario != id_instructor:
        raise HTTPException(status_code=403, detail="No autorizado para ver las programaciones de otro instructor")

    try:
        programaciones = crud_programacion.get_programaciones_by_instructor(db, id_instructor=id_instructor)
        return programaciones
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all", response_model=List[ProgramacionOut])
def get_all_programaciones(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todas las programaciones con paginación.
    Solo superadmin (1) y admin (2) pueden ver todas las programaciones.
    """
    if current_user.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado para ver todas las programaciones")

    try:
        programaciones = crud_programacion.get_all_programaciones(db, skip=skip, limit=limit)
        return programaciones
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detalle/{id_programacion}", response_model=ProgramacionOut)
def get_programacion_by_id(
    id_programacion: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene una programación específica por su ID.
    """
    try:
        programacion = crud_programacion.get_programacion_by_id(db, id_programacion=id_programacion)
        if programacion is None:
            raise HTTPException(status_code=404, detail="Programación no encontrada")
        return programacion
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint paramétrico general - debe ir después de los específicos
@router.get("/{cod_ficha}", response_model=List[ProgramacionOut])
def get_programaciones_by_ficha(
    cod_ficha: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Obtiene todas las programaciones de un grupo específico por cod_ficha.
    """
    try:
        programaciones = crud_programacion.get_programaciones_by_ficha(db, cod_ficha=cod_ficha)
        return programaciones
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ProgramacionOut, status_code=status.HTTP_201_CREATED)
def create_programacion(
    programacion: ProgramacionCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Crea una nueva programación.
    Solo superadmin (1), admin (2) e instructores (3) pueden crear programaciones.
    """
    if current_user.id_rol not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado para realizar esta acción")

    try:
        programacion_db = crud_programacion.create_programacion(db, programacion, current_user.id_usuario)
        if programacion_db is None:
            raise HTTPException(status_code=400, detail="Error al crear la programación")
        return programacion_db
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id_programacion}")
def update_programacion(
    id_programacion: int,
    programacion: ProgramacionUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Actualiza una programación existente.
    Solo superadmin (1), admin (2) e instructores (3) pueden actualizar programaciones.
    Los instructores solo pueden actualizar sus propias programaciones.
    """
    if current_user.id_rol not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado para realizar esta acción")

    # Verificar si el instructor puede actualizar esta programación
    if current_user.id_rol == 3:
        programacion_actual = crud_programacion.get_programacion_by_id(db, id_programacion)
        if programacion_actual is None:
            raise HTTPException(status_code=404, detail="Programación no encontrada")
        if programacion_actual.id_instructor != current_user.id_usuario:
            raise HTTPException(status_code=403, detail="No autorizado para actualizar esta programación")

    try:
        success = crud_programacion.update_programacion(db, id_programacion, programacion)
        if not success:
            raise HTTPException(status_code=404, detail="Programación no encontrada o sin cambios para aplicar")
        return {"message": "Programación actualizada correctamente"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_programacion}")
def delete_programacion(
    id_programacion: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Elimina una programación específica.
    Solo superadmin (1) y admin (2) pueden eliminar programaciones.
    """
    if current_user.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado para realizar esta acción")

    try:
        success = crud_programacion.delete_programacion(db, id_programacion)
        if not success:
            raise HTTPException(status_code=404, detail="Programación no encontrada")
        return {"message": "Programación eliminada correctamente"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) 