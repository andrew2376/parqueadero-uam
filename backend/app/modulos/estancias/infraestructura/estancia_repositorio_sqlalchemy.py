from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.modulos.estancias.dominio.estancia import Estancia
from app.modulos.estancias.dominio.estancia_repositorio import EstanciaRepositorio
from app.modulos.estancias.infraestructura.estancia_modelo import EstanciaModelo


class EstanciaRepositorioSQLAlchemy(EstanciaRepositorio):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def buscar_activa_por_placa(
        self,
        placa: str,
        sede_id: UUID,
    ) -> Estancia | None:

        modelo = (
            self.sesion.query(EstanciaModelo)
            .filter(
                EstanciaModelo.placa == placa,
                EstanciaModelo.sede_id == sede_id,
                EstanciaModelo.estado == "DENTRO",
                EstanciaModelo.fecha_hora_salida.is_(None),
            )
            .first()
        )

        if modelo is None:
            return None

        return self._convertir_a_dominio(modelo)

    def registrar_entrada(
        self,
        estancia: Estancia,
    ) -> Estancia:

        modelo = EstanciaModelo(
            sede_id=estancia.sede_id,
            placa=estancia.placa,
            tipo_vehiculo=estancia.tipo_vehiculo,
            fecha_hora_entrada=estancia.fecha_hora_entrada,
            fecha_hora_salida=None,
            estado="DENTRO",
        )

        self.sesion.add(modelo)
        self.sesion.flush()

        estancia_registrada = self._convertir_a_dominio(modelo)

        self.sesion.commit()

        return estancia_registrada

    def registrar_salida(
        self,
        estancia_id: UUID,
        fecha_hora_salida: datetime,
    ) -> bool:

        resultado = (
            self.sesion.query(EstanciaModelo)
            .filter(
                EstanciaModelo.id == estancia_id,
                EstanciaModelo.estado == "DENTRO",
                EstanciaModelo.fecha_hora_salida.is_(None),
            )
            .update(
                {
                    EstanciaModelo.fecha_hora_salida: fecha_hora_salida,
                    EstanciaModelo.estado: "SALIO",
                },
                synchronize_session=False,
            )
        )

        if resultado == 1:
            self.sesion.commit()
            return True

        self.sesion.rollback()
        return False

    @staticmethod
    def _convertir_a_dominio(
        modelo: EstanciaModelo,
    ) -> Estancia:

        return Estancia(
            id=modelo.id,
            sede_id=modelo.sede_id,
            placa=modelo.placa,
            tipo_vehiculo=modelo.tipo_vehiculo,
            fecha_hora_entrada=modelo.fecha_hora_entrada,
            fecha_hora_salida=modelo.fecha_hora_salida,
            estado=modelo.estado,
        )
