from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificacionBase(BaseModel):
    mensaje: str
    leida: bool = False


class NotificacionCreate(NotificacionBase):
    id_usuario: int


class Notificacion(NotificacionBase):
    id_notificacion: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True
