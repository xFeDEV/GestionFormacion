from pydantic import BaseModel
from typing import List

class GrupoInstructorBase(BaseModel):
    cod_ficha: int
    id_instructor: int

class GrupoInstructorCreate(GrupoInstructorBase):
    pass

class GrupoInstructorUpdate(BaseModel):
    cod_ficha: int
    id_instructor: int

class GrupoInstructorOut(GrupoInstructorBase):
    class Config:
        from_attributes = True