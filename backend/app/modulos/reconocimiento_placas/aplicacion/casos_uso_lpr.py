from uuid import UUID

from app.modulos.reconocimiento_placas.dominio.lector_lpr_puerto import LectorLPRPuerto
from app.modulos.reconocimiento_placas.dominio.lectura_lpr import (
    LecturaLPR,
    OrigenLectura,
)


class SimularLecturaPlaca:
    """
    Caso de uso para activar la simulación de lectura en un carril.
    """

    def __init__(self, lector: LectorLPRPuerto) -> None:
        self.lector = lector

    def ejecutar(self, carril_id: UUID) -> LecturaLPR:
        return self.lector.capturar_lectura(carril_id=carril_id)


class RegistrarLecturaManual:
    """
    Caso de uso para registrar o forzar una lectura manual cuando
    la cámara falla o tiene baja confianza (F-04).
    """

    def ejecutar(self, carril_id: UUID, placa: str) -> LecturaLPR:
        return LecturaLPR(
            carril_id=carril_id,
            placa=placa,
            confianza=100.0,
            origen=OrigenLectura.MANUAL,
        )
