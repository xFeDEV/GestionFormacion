from pydantic import BaseModel, Field
from typing import Optional

# --- Schema para Resultado de Aprendizaje ---
class ResultadoAprendizajeBase(BaseModel):
    cod_resultado: int
    nombre: str = Field(max_length=500)
    cod_competencia: int

class ResultadoAprendizajeCreate(ResultadoAprendizajeBase):
    pass

class ResultadoAprendizajeUpdate(BaseModel):
    nombre: Optional[str] = Field(max_length=500, default=None)
    cod_competencia: Optional[int] = None

class ResultadoAprendizajeOut(ResultadoAprendizajeBase):
    horas: Optional[int] = 0  # Horas asignadas al resultado (opcional)
    
    class Config:
        from_attributes = True
