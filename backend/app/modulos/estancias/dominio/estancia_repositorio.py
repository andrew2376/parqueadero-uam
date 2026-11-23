from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modulos.estancias.dominio.estancia import Estancia


class EstanciaRepositorio(ABC):
    @abstractmethod
    def buscar_activa_por_placa(
        self,
        placa: str,
        sede_id: UUID,
    ) -> Estancia | None:
        pass

    @abstractmethod
    def registrar_entrada(
        self,
        estancia: Estancia,
    ) -> Estancia:
        pass

    @abstractmethod
    def registrar_salida(
        self,
        estancia_id: UUID,
        fecha_hora_salida: datetime,
    ) -> bool:
        pass
