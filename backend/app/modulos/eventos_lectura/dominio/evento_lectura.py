from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class OrigenEventoLectura(str, Enum):
    AUTOMATICO = "AUTOMATICO"
    MANUAL = "MANUAL"


class EstadoEventoLectura(str, Enum):
    EXITOSA = "EXITOSA"
    BAJA_CONFIANZA = "BAJA_CONFIANZA"
    FALLIDA = "FALLIDA"


@dataclass
class EventoLectura:
    """
    Representa un evento de lectura de placa asociado
    a una sede y un carril del parqueadero.
    """

    sede_id: UUID
    carril_id: UUID
    placa: str | None
    confianza: float
    origen: OrigenEventoLectura
    estado: EstadoEventoLectura = EstadoEventoLectura.EXITOSA
    fecha_hora: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.placa is not None:
            self.placa = self.placa.strip().upper()

        if self.estado == EstadoEventoLectura.FALLIDA:
            self.placa = None
        elif not self.placa:
            raise ValueError("La placa es obligatoria para una lectura no fallida.")

        if not (0.0 <= self.confianza <= 100.0):
            raise ValueError("La confianza debe estar entre 0.0 y 100.0.")

        if self.fecha_hora.tzinfo is None:
            raise ValueError("La fecha del evento debe incluir zona horaria.")
