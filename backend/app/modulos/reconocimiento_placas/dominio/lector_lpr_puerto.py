from abc import ABC, abstractmethod
from uuid import UUID

from app.modulos.reconocimiento_placas.dominio.lectura_lpr import LecturaLPR


class LectorLPRPuerto(ABC):
    """
    Puerto hexagonal para interactuar con dispositivos o servicios LPR.
    Permite desacoplar el origen de la lectura (simulado, cámara RTSP o servicio OCR externo).
    """

    @abstractmethod
    def capturar_lectura(self, carril_id: UUID) -> LecturaLPR:
        """Captura una lectura de placa desde el dispositivo o simulación del carril indicado."""
        raise NotImplementedError
