from pydantic import BaseModel, Field
from typing import Optional

class AmbienteBase(BaseModel):
    nombre_ambiente: str = Field(max_length=40)
    num_max_aprendices: int
    municipio: str = Field(max_length=40)
    ubicacion: str = Field(max_length=80)
    cod_centro: int

class AmbienteCreate(AmbienteBase):
    estado: bool = True

class AmbienteUpdate(BaseModel):
    nombre_ambiente: Optional[str] = None
    num_max_aprendices: Optional[int] = None
    municipio: Optional[str] = None
    ubicacion: Optional[str] = None
    cod_centro: Optional[int] = None
    estado: Optional[bool] = None

class AmbienteOut(AmbienteBase):
    id_ambiente: int
    estado: bool

    class Config:
        from_attributes = True