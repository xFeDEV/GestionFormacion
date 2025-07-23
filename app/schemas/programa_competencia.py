from pydantic import BaseModel
from typing import Optional

# --- Schema para Programa Competencia ---
class ProgramaCompetenciaBase(BaseModel):
    cod_programa: int
    cod_competencia: int

class ProgramaCompetenciaCreate(ProgramaCompetenciaBase):
    pass

class ProgramaCompetenciaUpdate(BaseModel):
    cod_competencia: Optional[int] = None
    cod_programa: Optional[int] = None

class ProgramaCompetenciaOut(BaseModel):
    cod_prog_competencia: int  # AUTO_INCREMENT PRIMARY KEY
    cod_programa: int
    cod_competencia: int
    
    class Config:
        from_attributes = True
