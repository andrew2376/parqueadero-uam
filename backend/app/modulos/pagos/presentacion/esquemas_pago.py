from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PagoEfectivoCrear(BaseModel):
    cobro_id: UUID
    clave_idempotencia: str = Field(
        min_length=1,
        max_length=100,
    )
    valor: Decimal = Field(
        gt=0,
        decimal_places=2,
    )


class PagoRespuesta(BaseModel):
    id: UUID
    cobro_id: UUID
    medio_pago: str
    valor: Decimal
    fecha_hora_pago: datetime
    clave_idempotencia: str


class CobroConsultaRespuesta(BaseModel):
    cobro_id: UUID
    sede_id: UUID
    sede_nombre: str
    placa: str
    dia_operativo: date
    tarifa_aplicada: str
    valor_tarifa: Decimal
    pagado: bool
    pago_id: UUID | None = None
    fecha_hora_pago: datetime | None = None
    vehiculo_dentro: bool
