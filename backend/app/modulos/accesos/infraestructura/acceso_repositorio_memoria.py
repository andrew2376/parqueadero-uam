from uuid import UUID

from app.modulos.accesos.dominio.acceso_repositorio import AccesoRepositorio
from app.modulos.accesos.dominio.ingreso import EstadoAcceso, RegistroIngreso
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class AccesoRepositorioEnMemoria(AccesoRepositorio):
    """
    Implementación en memoria para el caso de uso de accesos, desacoplada
    de la base de datos hasta que se integre la tarea de persistencia S110.
    """

    def __init__(self) -> None:
        self._ingresos: list[RegistroIngreso] = []

    def guardar_ingreso(self, ingreso: RegistroIngreso) -> RegistroIngreso:
        self._ingresos.append(ingreso)
        return ingreso

    def buscar_ingreso_activo_por_placa(self, placa: str, sede_id: UUID) -> RegistroIngreso | None:
        for ing in self._ingresos:
            if ing.placa == placa and ing.sede_id == sede_id and ing.estado == EstadoAcceso.ACTIVO:
                return ing
        return None

    def contar_vehiculos_activos(self, sede_id: UUID, tipo_vehiculo: TipoVehiculo) -> int:
        return sum(
            1
            for ing in self._ingresos
            if ing.sede_id == sede_id and ing.tipo_vehiculo == tipo_vehiculo and ing.estado == EstadoAcceso.ACTIVO
        )


_repositorio_singleton = AccesoRepositorioEnMemoria()


def obtener_repositorio_acceso() -> AccesoRepositorio:
    return _repositorio_singleton
