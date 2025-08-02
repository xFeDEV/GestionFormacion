from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, time, timedelta

class ProgramacionBase(BaseModel):
    id_instructor: int
    cod_ficha: int
    fecha_programada: date
    horas_programadas: int
    hora_inicio: time
    hora_fin: time
    cod_competencia: int
    cod_resultado: int

class ProgramacionCreate(ProgramacionBase):
    pass

class ProgramacionUpdate(BaseModel):
    id_instructor: Optional[int] = None
    cod_ficha: Optional[int] = None
    fecha_programada: Optional[date] = None
    horas_programadas: Optional[int] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    cod_competencia: Optional[int] = None
    cod_resultado: Optional[int] = None

class ProgramacionOut(ProgramacionBase):
    id_programacion: int
    id_user: Optional[int] = None
    
    # Campos adicionales para mostrar información completa
    nombre_instructor: Optional[str] = None
    nombre_competencia: Optional[str] = None
    nombre_resultado: Optional[str] = None

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

# Esquemas para Competencias
class CompetenciaOut(BaseModel):
    cod_competencia: int
    nombre: str
    horas: Optional[int] = None

    class Config:
        from_attributes = True

# Esquemas para Resultados de Aprendizaje
class ResultadoAprendizajeOut(BaseModel):
    cod_resultado: int
    nombre: str
    cod_competencia: int

    class Config:
        from_attributes = True

# Esquemas para Validación de Cruce de Programación
class ValidarCruceRequest(BaseModel):
    id_instructor: int
    fecha_programada: date
    hora_inicio: time
    hora_fin: time
    id_programacion_actual: Optional[int] = None

class ValidarCruceResponse(BaseModel):
    conflicto: bool
    mensaje: Optional[str] = None 