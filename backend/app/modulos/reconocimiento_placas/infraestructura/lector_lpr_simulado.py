import random
from enum import StrEnum
from typing import ClassVar
from uuid import UUID

from app.modulos.reconocimiento_placas.dominio.lector_lpr_puerto import (
    LectorLPRPuerto,
)
from app.modulos.reconocimiento_placas.dominio.lectura_lpr import (
    LecturaLPR,
    OrigenLectura,
)


class EscenarioSimulacion(StrEnum):
    ALTA = "alta"
    BAJA = "baja"
    SIN_LECTURA = "sin-lectura"


class LectorLPRSimulado(LectorLPRPuerto):
    """
    Adaptador de prueba sustituible para el sistema LPR.
    Permite inyectar lecturas preconfiguradas o generar lecturas simuladas
    controladas para demostraciones académicas y pruebas de integración.
    """

    PLACAS_DEMO: ClassVar[list[str]] = [
        "ABC123",  # Carro
        "XYZ789",  # Carro
        "DEF45A",  # Moto
        "GHI67B",  # Moto
        "UAM100",  # Carro
    ]

    def __init__(
        self,
        placa_fija: str | None = None,
        confianza_fija: float | None = None,
    ) -> None:
        self.placa_fija = placa_fija
        self.confianza_fija = confianza_fija

    def establecer_proxima_lectura(
        self,
        placa: str,
        confianza: float = 95.0,
    ) -> None:
        """Permite que las pruebas o la UI fuercen una placa específica."""
        self.placa_fija = placa
        self.confianza_fija = confianza

    @classmethod
    def para_escenario(
        cls, escenario: EscenarioSimulacion, placa: str | None = None
    ) -> "LectorLPRSimulado":
        match escenario:
            case EscenarioSimulacion.ALTA:
                return cls(placa_fija=placa or "abc-123", confianza_fija=95.0)
            case EscenarioSimulacion.BAJA:
                return cls(placa_fija=placa or "def-45a", confianza_fija=55.0)
            case EscenarioSimulacion.SIN_LECTURA:
                return cls(placa_fija="", confianza_fija=0.0)

    def capturar_lectura(self, carril_id: UUID) -> LecturaLPR:
        placa = self.placa_fija if self.placa_fija is not None else random.choice(self.PLACAS_DEMO)

        confianza = (
            self.confianza_fija
            if self.confianza_fija is not None
            else round(random.uniform(85.0, 99.5), 1)
        )

        return LecturaLPR(
            carril_id=carril_id,
            placa=placa,
            confianza=confianza,
            origen=OrigenLectura.AUTOMATICO,
        )

    def simular_lectura_manual(
        self,
        carril_id: UUID,
        placa: str,
    ) -> LecturaLPR:
        """Simula una digitación directa por parte del operador."""
        return LecturaLPR(
            carril_id=carril_id,
            placa=placa,
            confianza=100.0,
            origen=OrigenLectura.MANUAL,
        )
