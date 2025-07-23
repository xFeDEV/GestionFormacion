from pydantic import BaseModel, Field
from typing import Optional

# --- Schema para Competencia ---
class CompetenciaBase(BaseModel):
    cod_competencia: int
    nombre: str = Field(max_length=500)
    horas: Optional[int] = 0

class CompetenciaCreate(CompetenciaBase):
    pass

class CompetenciaUpdate(BaseModel):
    nombre: Optional[str] = Field(max_length=500, default=None)
    horas: Optional[int] = None

class CompetenciaOut(CompetenciaBase):
    class Config:
        from_attributes = True
