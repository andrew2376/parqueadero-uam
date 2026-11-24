from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CapacidadesActualizar(BaseModel):
    cupos_carro: int = Field(ge=0)
    cupos_moto: int = Field(ge=0)


class CupoRespuesta(BaseModel):
    sede_id: UUID
    tipo_vehiculo: str
    capacidad: int
    ocupados: int
    disponibles: int

    model_config = ConfigDict(from_attributes=True)


class CapacidadesRespuesta(BaseModel):
    sede_id: UUID
    cupos_carro: int
    cupos_moto: int
