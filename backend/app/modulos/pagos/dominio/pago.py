
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Pago:
    id: UUID
    cobro_id: UUID
    medio_pago: str
    valor: Decimal
    fecha_hora_pago: datetime
    clave_idempotencia: str
