from pydantic import BaseModel
from datetime import date
from typing import List

class FestivoOut(BaseModel):
    festivo: date

    class Config:
        orm_mode = True

class FestivosResponse(BaseModel):
    festivos: List[date]
    domingos: List[date]
    total_dias: int

    class Config:
        orm_mode = True
