from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.modulos.tarifas.dominio.tarifa import Tarifa
from app.modulos.tarifas.dominio.tarifa_repositorio import TarifaRepositorio
from app.modulos.tarifas.infraestructura.tarifa_modelo import TarifaModelo


class TarifaRepositorioSQLAlchemy(TarifaRepositorio):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, tarifa: Tarifa) -> Tarifa:
        """
        Registra una nueva versión sin sobrescribir las anteriores.

        Si existe una versión abierta anterior, cierra su vigencia
        en la fecha de inicio de la nueva versión.
        """

        try:
            modelos = (
                self.sesion.query(TarifaModelo)
                .filter(
                    TarifaModelo.sede_id == tarifa.sede_id,
                    TarifaModelo.tipo_vehiculo == tarifa.tipo_vehiculo,
                )
                .with_for_update()
                .all()
            )

            # Calcular automáticamente el siguiente número de versión.
            ultima_version = max(
                (modelo.version for modelo in modelos),
                default=0,
            )

            tarifa.version = ultima_version + 1

            # Cerrar las versiones abiertas anteriores.
            for modelo in modelos:
                if (
                    modelo.activa
                    and modelo.vigencia_hasta is None
                    and modelo.vigencia_desde < tarifa.vigencia_desde
                ):
                    modelo.vigencia_hasta = tarifa.vigencia_desde
                    modelo.activa = False

            # Comprobar que la nueva vigencia no se superponga
            # con ninguna versión existente.
            for modelo in modelos:
                hay_superposicion = (
                    tarifa.vigencia_hasta is None or modelo.vigencia_desde < tarifa.vigencia_hasta
                ) and (
                    modelo.vigencia_hasta is None or modelo.vigencia_hasta > tarifa.vigencia_desde
                )

                if hay_superposicion:
                    raise ValueError(
                        "La vigencia de la nueva tarifa se superpone con una versión existente."
                    )

            modelo_nuevo = TarifaModelo(
                id=tarifa.id,
                sede_id=tarifa.sede_id,
                tipo_vehiculo=tarifa.tipo_vehiculo,
                version=tarifa.version,
                tarifa_diurna=tarifa.tarifa_diurna,
                tarifa_nocturna=tarifa.tarifa_nocturna,
                vigencia_desde=tarifa.vigencia_desde,
                vigencia_hasta=tarifa.vigencia_hasta,
                activa=tarifa.activa,
            )

            self.sesion.add(modelo_nuevo)
            self.sesion.flush()

            tarifa_guardada = self._convertir_a_dominio(modelo_nuevo)

            self.sesion.commit()

            return tarifa_guardada

        except Exception:
            self.sesion.rollback()
            raise

    def buscar_por_sede_y_tipo(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Tarifa | None:
        """
        Busca la versión activa más reciente de una tarifa
        para una sede y tipo de vehículo.
        """

        modelo = (
            self.sesion.query(TarifaModelo)
            .filter(
                TarifaModelo.sede_id == sede_id,
                TarifaModelo.tipo_vehiculo == tipo_vehiculo.strip().upper(),
                TarifaModelo.activa.is_(True),
            )
            .order_by(TarifaModelo.version.desc())
            .first()
        )

        if modelo is None:
            return None

        return self._convertir_a_dominio(modelo)

    def buscar_vigente(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
        fecha: datetime,
    ) -> Tarifa | None:
        """
        Busca la versión cuya vigencia contiene la fecha indicada.

        IMPORTANTE:
        No se filtra por activa, porque las versiones históricas
        se marcan como inactivas al cerrar su vigencia, pero deben
        seguir disponibles para consultas de fechas anteriores.
        """

        modelo = (
            self.sesion.query(TarifaModelo)
            .filter(
                TarifaModelo.sede_id == sede_id,
                TarifaModelo.tipo_vehiculo == tipo_vehiculo.strip().upper(),
                TarifaModelo.vigencia_desde <= fecha,
                ((TarifaModelo.vigencia_hasta.is_(None)) | (TarifaModelo.vigencia_hasta > fecha)),
            )
            .order_by(TarifaModelo.version.desc())
            .first()
        )

        if modelo is None:
            return None

        return self._convertir_a_dominio(modelo)

    def listar_por_sede(self, sede_id: UUID) -> list[Tarifa]:
        """
        Lista todas las versiones de tarifas registradas en una sede.
        """

        modelos = (
            self.sesion.query(TarifaModelo)
            .filter(TarifaModelo.sede_id == sede_id)
            .order_by(
                TarifaModelo.tipo_vehiculo,
                TarifaModelo.version.desc(),
            )
            .all()
        )

        return [self._convertir_a_dominio(modelo) for modelo in modelos]

    def listar_versiones(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> list[Tarifa]:
        """
        Lista todas las versiones de una tarifa, incluidas las históricas.
        """

        modelos = (
            self.sesion.query(TarifaModelo)
            .filter(
                TarifaModelo.sede_id == sede_id,
                TarifaModelo.tipo_vehiculo == tipo_vehiculo.strip().upper(),
            )
            .order_by(TarifaModelo.version.desc())
            .all()
        )

        return [self._convertir_a_dominio(modelo) for modelo in modelos]

    def cerrar_vigencia(
        self,
        tarifa_id: UUID,
        fecha_fin: datetime,
    ) -> Tarifa:
        """
        Cierra la vigencia de una versión de tarifa.
        """

        try:
            modelo = (
                self.sesion.query(TarifaModelo)
                .filter(TarifaModelo.id == tarifa_id)
                .with_for_update()
                .first()
            )

            if modelo is None:
                raise ValueError("La tarifa indicada no existe.")

            if fecha_fin <= modelo.vigencia_desde:
                raise ValueError(
                    "La fecha final debe ser posterior a la fecha inicial de vigencia."
                )

            if modelo.vigencia_hasta is not None:
                raise ValueError("La vigencia de esta tarifa ya fue cerrada.")

            modelo.vigencia_hasta = fecha_fin
            modelo.activa = False

            self.sesion.flush()

            tarifa_actualizada = self._convertir_a_dominio(modelo)

            self.sesion.commit()

            return tarifa_actualizada

        except Exception:
            self.sesion.rollback()
            raise

    @staticmethod
    def _convertir_a_dominio(modelo: TarifaModelo) -> Tarifa:
        """
        Convierte el modelo de infraestructura a la entidad de dominio.
        """

        return Tarifa(
            id=modelo.id,
            sede_id=modelo.sede_id,
            tipo_vehiculo=modelo.tipo_vehiculo,
            tarifa_diurna=modelo.tarifa_diurna,
            tarifa_nocturna=modelo.tarifa_nocturna,
            activa=modelo.activa,
            version=modelo.version,
            vigencia_desde=modelo.vigencia_desde,
            vigencia_hasta=modelo.vigencia_hasta,
        )
