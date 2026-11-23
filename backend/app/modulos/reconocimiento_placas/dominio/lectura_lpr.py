from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from app.modulos.vehiculos.dominio.vehiculo import (
    TipoVehiculo,
    clasificar_placa,
    normalizar_placa,
)


class OrigenLectura(str, Enum):
    AUTOMATICO = "AUTOMATICO"
    MANUAL = "MANUAL"


class EstadoLectura(str, Enum):
    EXITOSA = "EXITOSA"
    BAJA_CONFIANZA = "BAJA_CONFIANZA"
    FALLIDA = "FALLIDA"


@dataclass
class LecturaLPR:
    """
    Representa el resultado de una captura de placa por la cámara
    o ingresada manualmente por el operador.
    """

    carril_id: UUID
    placa: str
    confianza: float
    origen: OrigenLectura = OrigenLectura.AUTOMATICO
    tipo_vehiculo: TipoVehiculo | None = None
    estado: EstadoLectura = EstadoLectura.EXITOSA
    id: UUID = field(default_factory=uuid4)
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.placa = normalizar_placa(self.placa)

        # Validación de rango de confianza (0.0 a 100.0%)
        if not (0.0 <= self.confianza <= 100.0):
            raise ValueError(
                f"El porcentaje de confianza debe estar entre 0.0 y 100.0, recibido: {self.confianza}"
            )

        # Si la placa está vacía, la lectura es fallida
        if not self.placa:
            self.estado = EstadoLectura.FALLIDA
            self.tipo_vehiculo = None
            return

        # Clasificación automática de placa
        try:
            self.tipo_vehiculo = clasificar_placa(self.placa)
        except ValueError:
            self.estado = EstadoLectura.FALLIDA
            self.tipo_vehiculo = None
            return

        # Umbral configurable por defecto: si es menor al 70%, es baja confianza
        if self.confianza < 70.0:
            self.estado = EstadoLectura.BAJA_CONFIANZA
        else:
            self.estado = EstadoLectura.EXITOSA

    @property
    def requiere_confirmacion_manual(self) -> bool:
        """Determina si el operador debe validar o corregir la placa."""
        return self.estado in (EstadoLectura.BAJA_CONFIANZA, EstadoLectura.FALLIDA)
