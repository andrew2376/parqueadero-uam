from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from app.modulos.vehiculos.dominio.vehiculo import (
    TipoVehiculo,
    clasificar_placa,
    normalizar_placa,
)

UMBRAL_CONFIANZA_DEFECTO: float = 70.0


class OrigenLectura(str, Enum):
    AUTOMATICO = "AUTOMATICO"
    MANUAL = "MANUAL"
    CONFIRMADA_OPERADOR = "CONFIRMADA_OPERADOR"


class EstadoLectura(str, Enum):
    EXITOSA = "EXITOSA"
    BAJA_CONFIANZA = "BAJA_CONFIANZA"
    FALLIDA = "FALLIDA"


@dataclass
class LecturaLPR:
    """
    Representa el resultado de una captura de placa por la cámara
    o ingresada/confirmada manualmente por el operador (S109 / S201).
    """

    carril_id: UUID
    placa: str
    confianza: float
    origen: OrigenLectura = OrigenLectura.AUTOMATICO
    tipo_vehiculo: TipoVehiculo | None = None
    estado: EstadoLectura = EstadoLectura.EXITOSA
    umbral_confianza: float = UMBRAL_CONFIANZA_DEFECTO
    placa_original_detectada: str | None = None
    operador_id: str | None = None
    id: UUID = field(default_factory=uuid4)
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.placa = normalizar_placa(self.placa)

        # Validación de rango de confianza (0.0 a 100.0%)
        if not (0.0 <= self.confianza <= 100.0):
            raise ValueError(
                f"El porcentaje de confianza debe estar entre 0.0 y 100.0, recibido: {self.confianza}"
            )

        # Si el origen es manual o confirmado por operador, la confianza es 100%
        if self.origen in (OrigenLectura.MANUAL, OrigenLectura.CONFIRMADA_OPERADOR):
            self.confianza = 100.0
            self.estado = EstadoLectura.EXITOSA

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

        # Umbral configurable para lecturas automáticas
        if self.origen == OrigenLectura.AUTOMATICO:
            if self.confianza < self.umbral_confianza:
                self.estado = EstadoLectura.BAJA_CONFIANZA
            else:
                self.estado = EstadoLectura.EXITOSA

    @property
    def requiere_confirmacion_manual(self) -> bool:
        """Determina si el operador debe validar o corregir la placa."""
        return self.estado in (EstadoLectura.BAJA_CONFIANZA, EstadoLectura.FALLIDA)

    def confirmar_por_operador(self, placa_confirmada: str, operador_id: str) -> None:
        """
        Permite al operador confirmar la placa leída o corregirla manualmente (S201).
        """
        placa_normalizada = normalizar_placa(placa_confirmada)
        if not placa_normalizada:
            raise ValueError("La placa confirmada no puede estar vacía.")

        tipo = clasificar_placa(placa_normalizada)

        self.placa_original_detectada = self.placa
        self.placa = placa_normalizada
        self.tipo_vehiculo = tipo
        self.operador_id = operador_id
        self.confianza = 100.0
        self.origen = OrigenLectura.CONFIRMADA_OPERADOR
        self.estado = EstadoLectura.EXITOSA
