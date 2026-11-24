from uuid import UUID

from app.modulos.reconocimiento_placas.dominio.lector_lpr_puerto import LectorLPRPuerto
from app.modulos.reconocimiento_placas.dominio.lectura_lpr import (
    LecturaLPR,
    OrigenLectura,
)


class SimularLecturaPlaca:
    """
    Caso de uso para activar la simulación de lectura en un carril (S109).
    """

    def __init__(self, lector: LectorLPRPuerto) -> None:
        self.lector = lector

    def ejecutar(self, carril_id: UUID) -> LecturaLPR:
        return self.lector.capturar_lectura(carril_id=carril_id)


class RegistrarLecturaManual:
    """
    Caso de uso para registrar o forzar una lectura manual cuando
    la cámara falla o no hay lectura previa (F-04 / S109).
    """

    def ejecutar(self, carril_id: UUID, placa: str) -> LecturaLPR:
        return LecturaLPR(
            carril_id=carril_id,
            placa=placa,
            confianza=100.0,
            origen=OrigenLectura.MANUAL,
        )


class ValidarLecturaBajaConfianza:
    """
    Caso de uso para validar, confirmar o corregir una lectura previa de
    baja confianza (< umbral) por parte del operador (S201).
    """

    def ejecutar(
        self,
        carril_id: UUID,
        placa_confirmada: str,
        operador_id: str,
        placa_detectada_previa: str | None = None,
        confianza_previa: float = 50.0,
        umbral_confianza: float = 70.0,
    ) -> LecturaLPR:
        lectura = LecturaLPR(
            carril_id=carril_id,
            placa=placa_detectada_previa or placa_confirmada,
            confianza=confianza_previa,
            origen=OrigenLectura.AUTOMATICO,
            umbral_confianza=umbral_confianza,
        )

        lectura.confirmar_por_operador(
            placa_confirmada=placa_confirmada,
            operador_id=operador_id,
        )
        return lectura
