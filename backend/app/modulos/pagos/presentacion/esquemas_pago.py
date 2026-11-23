from datetime import datetime
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
