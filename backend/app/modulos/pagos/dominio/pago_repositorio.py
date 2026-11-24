from abc import ABC, abstractmethod
from uuid import UUID

from app.modulos.pagos.dominio.pago import Pago


class PagoRepositorio(ABC):
    @abstractmethod
    def buscar_por_clave_idempotencia(
        self,
        clave_idempotencia: str,
    ) -> Pago | None:
        """Busca un pago previamente registrado por su clave idempotente."""
        raise NotImplementedError

    @abstractmethod
    def buscar_por_cobro(
        self,
        cobro_id: UUID,
    ) -> Pago | None:
        """Busca el pago asociado a un cobro."""
        raise NotImplementedError

    @abstractmethod
    def guardar(
        self,
        pago: Pago,
    ) -> Pago:
        """Registra un nuevo pago."""
        raise NotImplementedError
