from pydantic import BaseModel, Field

# --- Schema para CentroFormacion ---
class CentroFormacionBase(BaseModel):
    cod_centro: int
    nombre_centro: str = Field(max_length=80)
    cod_regional: int

# --- Modelo para carga masiva ---
class CentroFormacionCreate(CentroFormacionBase):
    pass  # No changes needed since cod_centro is already required in CentroFormacionBase

class CentroFormacionOut(CentroFormacionBase):
    pass
    class Config:
            # Permite que Pydantic lea los datos directamente de un objeto de base de datos
            from_attributes = True