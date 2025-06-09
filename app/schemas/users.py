from pydantic import  BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    nombre_completo: str = Field(min_length=3, max_length=80)
    identificacion: str = Field(min_length=6, max_length=12)
    id_rol: int
    correo: EmailStr
    tipo_contrato: str = Field(min_length=6, max_length=50)
    telefono: str = Field(min_length=7, max_length=15)
    estado: bool
    cod_centro: int

class UserCreate(UserBase):
    pass_hash: str = Field(min_length=8, max_length=50)

class UserUpdate(BaseModel):
    nombre_completo: Optional[str] = Field(default=None, min_length=3, max_length=80)
    tipo_contrato: Optional[str] = Field(default=None, min_length=6, max_length=50)
    telefono: Optional[str] = Field(default=None, min_length=7, max_length=15)
    correo: Optional[EmailStr] = Field(default=None, min_length=7, max_length=100)
    # estado: Optional[bool] = None

class UserOut(UserBase):
    id_usuario: int
    nombre_rol: Optional[str] = None
