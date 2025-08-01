from pydantic import BaseModel, Field
from typing import Optional, List

class ProgramaBase(BaseModel):
    cod_programa: int
    la_version: int
    nombre: str = Field(max_length=255)
    horas_lectivas: int
    horas_productivas: int

class ProgramaFormacionCreate(BaseModel):
    cod_programa: int
    la_version: int
    nombre: str = Field(max_length=255)
    horas_lectivas: Optional[int] = None
    horas_productivas: Optional[int] = None

class ProgramaCreate(ProgramaBase):
    pass

class ProgramaUpdate(BaseModel):
    horas_lectivas: Optional[int] = None
    horas_productivas: Optional[int] = None

class ProgramaOut(ProgramaBase):
    class Config:
        # Permite que Pydantic lea los datos de un objeto de base de datos
        from_attributes = True

class ProgramaPage(BaseModel):
    total_items: int
    items: List[ProgramaOut]