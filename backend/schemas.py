from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class TipoProyectoBase(BaseModel):
    tipo_proyecto_id: int
    nombre: str

    class Config:
        orm_mode = True

class ProyectoBase(BaseModel):
    fact_id: int
    proyecto_id: int
    nombre: str
    descripcion: Optional[str] = None
    tipo_proyecto: Optional[TipoProyectoBase] = None

    class Config:
        orm_mode = True
