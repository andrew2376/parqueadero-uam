from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modulos.cupos.dominio.cupo import Cupo
from app.modulos.cupos.dominio.cupo_repositorio import CupoRepositorio
from app.modulos.estancias.infraestructura.estancia_modelo import EstanciaModelo
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo


class CupoRepositorioSQLAlchemy(CupoRepositorio):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def consultar_disponibilidad(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Cupo:
        return self._obtener_cupo(sede_id, tipo_vehiculo, bloquear=False)

    def reservar_cupo(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Cupo:
        cupo = self._obtener_cupo(sede_id, tipo_vehiculo, bloquear=True)

        if cupo.esta_lleno:
            raise ValueError(f"No hay cupos disponibles para {cupo.tipo_vehiculo.lower()}.")

        # No se confirma aquí la transacción.
        # El bloqueo debe mantenerse hasta que se registre la estancia
        # utilizando esta misma sesión.
        return cupo

    def _obtener_cupo(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
        bloquear: bool,
    ) -> Cupo:
        tipo = tipo_vehiculo.strip().upper()

        if tipo not in {"CARRO", "MOTO"}:
            raise ValueError("El tipo de vehículo debe ser CARRO o MOTO.")

        consulta_sede = select(SedeModelo).where(SedeModelo.id == sede_id)

        if bloquear:
            consulta_sede = consulta_sede.with_for_update()

        sede = self.sesion.execute(consulta_sede).scalar_one_or_none()

        if sede is None:
            raise ValueError("La sede especificada no existe.")

        capacidad = sede.cupos_carro if tipo == "CARRO" else sede.cupos_moto

        ocupados = (
            self.sesion.query(func.count(EstanciaModelo.id))
            .filter(
                EstanciaModelo.sede_id == sede_id,
                EstanciaModelo.tipo_vehiculo == tipo,
                EstanciaModelo.estado == "DENTRO",
                EstanciaModelo.fecha_hora_salida.is_(None),
            )
            .scalar()
        )

        return Cupo(
            sede_id=sede_id,
            tipo_vehiculo=tipo,
            capacidad=capacidad,
            ocupados=ocupados or 0,
        )
