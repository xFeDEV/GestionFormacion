from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, time, timedelta

# --- Schema para DatosGrupo ---
class GrupoBase(BaseModel):
    cod_ficha: Optional[int] = None
    num_aprendices_masculinos: Optional[int] = None
    num_aprendices_femenino: Optional[int] = None
    num_aprendices_no_binario: Optional[int] = None
    num_total_aprendices: Optional[int] = None
    num_total_aprendices_activos: Optional[int] = None
    # Campos adicionales del archivo DF-14
    cupo_total: Optional[int] = None
    en_transito: Optional[int] = None
    induccion: Optional[int] = None
    formacion: Optional[int] = None
    condicionado: Optional[int] = None
    aplazado: Optional[int] = None
    retiro_voluntario: Optional[int] = None
    cancelado: Optional[int] = None
    cancelamiento_vit_comp: Optional[int] = None
    desercion_vit_comp: Optional[int] = None
    por_certificar: Optional[int] = None
    certificados: Optional[int] = None
    traslados: Optional[int] = None
    otro: Optional[int] = None

class GrupoCreate(GrupoBase):
    pass

# --- Schema para actualizar (el cuerpo del PUT) ---
class GrupoUpdate(BaseModel):
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    id_ambiente: Optional[int] = None

# --- Schema para mostrar los datos (la respuesta del GET) ---
class GrupoOut(BaseModel):
    cod_ficha: int
    cod_centro: Optional[int] = None
    cod_programa: Optional[int] = None
    la_version: Optional[int] = None
    estado_grupo: Optional[str] = None
    nombre_nivel: Optional[str] = None
    jornada: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    etapa: Optional[str] = None
    modalidad: Optional[str] = None
    responsable: Optional[str] = None
    nombre_empresa: Optional[str] = None
    nombre_municipio: Optional[str] = None
    nombre_programa_especial: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    id_ambiente: Optional[int] = None  # <-- Correcto: id_ambiente como opcional

    # Validador para convertir el 'timedelta' de la DB a un 'time'
    @field_validator('hora_inicio', 'hora_fin', mode='before')
    @classmethod
    def format_time(cls, v):
        if isinstance(v, timedelta):
            # Convierte 00:00:00 (timedelta) a un objeto time
            total_seconds = int(v.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return time(hours % 24, minutes, seconds)
        return v

    class Config:
        # Permite que Pydantic lea los datos directamente de un objeto de base de datos
        from_attributes = True

# --- Schema enriquecido para mostrar datos con información relacionada ---
class GrupoEnriched(GrupoOut):
    """Schema enriquecido que incluye nombres de tablas relacionadas"""
    nombre_programa: Optional[str] = None
    nombre_ambiente: Optional[str] = None

    class Config:
        from_attributes = True 

# --- Schema para Regional ---
class RegionalCreate(BaseModel):
    cod_regional: int
    nombre: str

# --- Schema para búsqueda de grupos en select ---
class GrupoSelect(BaseModel):
    cod_ficha: int
    estado_grupo: Optional[str] = None
    jornada: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    etapa: Optional[str] = None
    responsable: Optional[str] = None
    nombre_programa: Optional[str] = None
    nombre_ambiente: Optional[str] = None

    class Config:
        from_attributes = True

# --- Schema para búsqueda avanzada con información adicional ---
class GrupoAdvancedOut(GrupoOut):
    """Schema para búsqueda avanzada que incluye información adicional de programas"""
    programa_nombre: Optional[str] = None

    class Config:
        from_attributes = True

# --- Schemas para el Dashboard ---

class DashboardKPISchema(BaseModel):
    """ Schema para la tarjeta de KPI de total de grupos. """
    total_grupo: int
    total_aprendices_formacion: int

class GruposPorMunicipioSchema(BaseModel):
    municipio: str
    cantidad: int
    total_aprendices_formacion: int

class GruposPorJornadaSchema(BaseModel):
    jornada: str
    cantidad: int
    total_aprendices_formacion: int

class GruposPorModalidadSchema(BaseModel):
    modalidad: str
    cantidad: int
    total_aprendices_formacion: int

class GruposPorEtapaSchema(BaseModel):
    etapa: str
    cantidad: int
    total_aprendices_formacion: int

class GruposPorNivelSchema(BaseModel):
    nivel: str
    cantidad: int
    total_aprendices_formacion: int

# --- Schema para respuesta paginada de grupos ---
class GrupoPage(BaseModel):
    total_items: int
    items: List[GrupoOut]

# --- Schema para respuesta paginada de búsqueda avanzada ---
class GrupoAdvancedPage(BaseModel):
    total_items: int
    items: List[GrupoAdvancedOut]