from datetime import datetime
from uuid import UUID

from app.modulos.estancias.dominio.estancia import Estancia
from app.modulos.estancias.dominio.estancia_repositorio import EstanciaRepositorio
from app.modulos.vehiculos.dominio.vehiculo import normalizar_placa


class RegistrarEntrada:
    def __init__(self, repositorio: EstanciaRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        placa: str,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Estancia:

        placa_normalizada = normalizar_placa(placa)

        estancia_activa = self.repositorio.buscar_activa_por_placa(
            placa_normalizada,
            sede_id,
        )

        if estancia_activa is not None:
            raise ValueError("El vehículo ya tiene una estancia activa en esta sede.")

        estancia = Estancia(
            id=None,
            sede_id=sede_id,
            placa=placa_normalizada,
            tipo_vehiculo=tipo_vehiculo.upper(),
            fecha_hora_entrada=datetime.now().astimezone(),
            fecha_hora_salida=None,
            estado="DENTRO",
        )

        return self.repositorio.registrar_entrada(estancia)
