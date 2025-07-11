from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, time, timedelta

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