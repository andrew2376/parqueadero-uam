
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modulos.carriles.dominio.carril import TipoCarril


class CarrilCrear(BaseModel):
    sede_id: UUID
    nombre: str = Field(min_length=1, max_length=80)
    tipo: TipoCarril


class CarrilActualizar(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    tipo: TipoCarril


class CarrilCambiarEstado(BaseModel):
    activo: bool


class CarrilRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sede_id: UUID
    nombre: str
    tipo: TipoCarril
    activo: bool
