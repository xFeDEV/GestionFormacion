from pydantic import BaseModel
from typing import Optional
from datetime import date

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

# Esquemas para respuestas detalladas
class InstructorDetallado(BaseModel):
    cod_ficha: int
    id_instructor: int
    nombre_completo: str
    correo: str
    identificacion: str
    telefono: str
    tipo_contrato: str
    nombre_rol: str
    
    class Config:
        from_attributes = True

class GrupoDetallado(BaseModel):
    cod_ficha: int
    id_instructor: int
    estado_grupo: Optional[str] = None
    jornada: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    etapa: Optional[str] = None
    nombre_programa: Optional[str] = None
    nombre_centro: Optional[str] = None
    
    class Config:
        from_attributes = True