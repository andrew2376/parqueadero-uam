from app.modulos.vehiculos.dominio.vehiculo import (
    Vehiculo,
    clasificar_placa,
    normalizar_placa,
)
from app.modulos.vehiculos.dominio.vehiculo_repositorio import VehiculoRepositorio


class RegistrarVehiculo:
    """
    Caso de uso para registrar o validar un vehículo asegurando
    la clasificación correcta según el formato de la placa.
    """

    def __init__(self, repositorio: VehiculoRepositorio | None = None) -> None:
        self.repositorio = repositorio

    def ejecutar(self, placa_raw: str) -> Vehiculo:
        placa = normalizar_placa(placa_raw)
        tipo = clasificar_placa(placa)

        if self.repositorio:
            existente = self.repositorio.buscar_por_placa(placa)
            if existente:
                return existente

        vehiculo = Vehiculo(placa=placa, tipo=tipo)

        if self.repositorio:
            self.repositorio.guardar(vehiculo)

        return vehiculo


class ClasificarPlaca:
    """
    Caso de uso simple para clasificar una placa sin persistencia.
    """

    def ejecutar(self, placa_raw: str) -> dict[str, str]:
        placa = normalizar_placa(placa_raw)
        tipo = clasificar_placa(placa)
        return {
            "placa": placa,
            "tipo": tipo.value,
        }
