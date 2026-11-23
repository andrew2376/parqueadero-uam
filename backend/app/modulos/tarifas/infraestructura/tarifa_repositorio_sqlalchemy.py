from uuid import UUID

from sqlalchemy.orm import Session

from app.modulos.tarifas.dominio.tarifa import Tarifa
from app.modulos.tarifas.dominio.tarifa_repositorio import TarifaRepositorio
from app.modulos.tarifas.infraestructura.tarifa_modelo import TarifaModelo


class TarifaRepositorioSQLAlchemy(TarifaRepositorio):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, tarifa: Tarifa) -> Tarifa:
        modelo = (
            self.sesion.query(TarifaModelo)
            .filter(
                TarifaModelo.sede_id == tarifa.sede_id,
                TarifaModelo.tipo_vehiculo == tarifa.tipo_vehiculo,
            )
            .first()
        )

        if modelo is None:
            modelo = TarifaModelo(
                id=tarifa.id,
                sede_id=tarifa.sede_id,
                tipo_vehiculo=tarifa.tipo_vehiculo,
                tarifa_diurna=tarifa.tarifa_diurna,
                tarifa_nocturna=tarifa.tarifa_nocturna,
                activa=tarifa.activa,
            )

            self.sesion.add(modelo)
        else:
            modelo.tarifa_diurna = tarifa.tarifa_diurna
            modelo.tarifa_nocturna = tarifa.tarifa_nocturna
            modelo.activa = tarifa.activa

        self.sesion.flush()

        tarifa_guardada = self._convertir_a_dominio(modelo)

        self.sesion.commit()

        return tarifa_guardada

    def buscar_por_sede_y_tipo(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Tarifa | None:

        modelo = (
            self.sesion.query(TarifaModelo)
            .filter(
                TarifaModelo.sede_id == sede_id,
                TarifaModelo.tipo_vehiculo == tipo_vehiculo.strip().upper(),
            )
            .first()
        )

        if modelo is None:
            return None

        return self._convertir_a_dominio(modelo)

    def listar_por_sede(self, sede_id: UUID) -> list[Tarifa]:
        modelos = (
            self.sesion.query(TarifaModelo)
            .filter(TarifaModelo.sede_id == sede_id)
            .order_by(TarifaModelo.tipo_vehiculo)
            .all()
        )

        return [self._convertir_a_dominio(modelo) for modelo in modelos]

    @staticmethod
    def _convertir_a_dominio(modelo: TarifaModelo) -> Tarifa:
        return Tarifa(
            id=modelo.id,
            sede_id=modelo.sede_id,
            tipo_vehiculo=modelo.tipo_vehiculo,
            tarifa_diurna=modelo.tarifa_diurna,
            tarifa_nocturna=modelo.tarifa_nocturna,
            activa=modelo.activa,
        )
