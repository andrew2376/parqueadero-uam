from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TarifaCrear(BaseModel):
    sede_id: UUID
    tipo_vehiculo: str = Field(pattern="^(CARRO|MOTO)$")
    tarifa_diurna: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    tarifa_nocturna: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    vigencia_desde: datetime | None = None

    @model_validator(mode="after")
    def validar_reglas_tarifarias(self):
        es_moto_gratuita = (
            self.tipo_vehiculo == "MOTO"
            and self.tarifa_diurna == Decimal("0")
            and self.tarifa_nocturna == Decimal("0")
        )

        if not es_moto_gratuita and self.tarifa_nocturna >= self.tarifa_diurna:
            raise ValueError(
                "La tarifa nocturna debe ser estrictamente menor que la tarifa diurna."
            )

        return self


class TarifaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sede_id: UUID
    tipo_vehiculo: str
    version: int
    tarifa_diurna: Decimal
    tarifa_nocturna: Decimal
    vigencia_desde: datetime
    vigencia_hasta: datetime | None
    activa: bool


class TarifaCerrarVigencia(BaseModel):
    vigencia_hasta: datetime


class TarifaCalculoRespuesta(BaseModel):
    sede_id: UUID
    tarifa_id: UUID
    version_tarifa: int
    tipo_vehiculo: str
    franja_horaria: str
    tarifa_aplicada: str
    valor_tarifa: Decimal
    fecha_hora: datetime
