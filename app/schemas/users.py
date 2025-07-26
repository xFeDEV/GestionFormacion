from pydantic import  BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

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
from pydantic import BaseModel

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str
class UserOut(UserBase):
    id_usuario: int
    nombre_rol: Optional[str] = None
    password_changed_at: Optional[datetime] = None
