from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.modulos.cupos.infraestructura.cupo_repositorio_sqlalchemy import (
    CupoRepositorioSQLAlchemy,
)
from app.modulos.estancias.dominio.estancia import Estancia
from app.modulos.estancias.dominio.estancia_repositorio import EstanciaRepositorio
from app.modulos.vehiculos.dominio.vehiculo import normalizar_placa


class RegistrarEntrada:
    def __init__(
        self,
        repositorio: EstanciaRepositorio,
        sesion: Session,
    ):
        self.repositorio = repositorio
        self.sesion = sesion
        self.cupo_repositorio = CupoRepositorioSQLAlchemy(sesion)

    def ejecutar(
        self,
        placa: str,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Estancia:
        try:
            placa_normalizada = normalizar_placa(placa)
            tipo = tipo_vehiculo.strip().upper()

            # 1. Bloquear la sede y validar la disponibilidad del cupo.
            # El bloqueo se mantiene hasta confirmar o revertir la transacción.
            self.cupo_repositorio.reservar_cupo(
                sede_id=sede_id,
                tipo_vehiculo=tipo,
            )

            # 2. Verificar que el vehículo no tenga otra estancia activa.
            estancia_activa = self.repositorio.buscar_activa_por_placa(
                placa_normalizada,
                sede_id,
            )

            if estancia_activa is not None:
                raise ValueError("El vehículo ya tiene una estancia activa en esta sede.")

            # 3. Crear la estancia.
            estancia = Estancia(
                id=None,
                sede_id=sede_id,
                placa=placa_normalizada,
                tipo_vehiculo=tipo,
                fecha_hora_entrada=datetime.now().astimezone(),
                fecha_hora_salida=None,
                estado="DENTRO",
            )

            # 4. Registrar la estancia en la misma transacción.
            estancia_registrada = self.repositorio.registrar_entrada(estancia)

            # 5. Confirmar la operación y liberar el bloqueo de la sede.
            self.sesion.commit()

            return estancia_registrada

        except Exception:
            self.sesion.rollback()
            raise
