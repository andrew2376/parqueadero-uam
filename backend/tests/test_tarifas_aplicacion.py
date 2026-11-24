
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.modulos.tarifas.aplicacion.calcular_tarifa import CalcularTarifa
from app.modulos.tarifas.aplicacion.configurar_tarifa import ConfigurarTarifa
from app.modulos.tarifas.dominio.franja_horaria import FranjaHoraria
from app.modulos.tarifas.dominio.tarifa import Tarifa


class TarifaRepositorioMemoria:
    def __init__(self):
        self.tarifas = {}

    def guardar(self, tarifa: Tarifa) -> Tarifa:
        clave = (tarifa.sede_id, tarifa.tipo_vehiculo)
        versiones = self.tarifas.setdefault(clave, [])

        # Calcular automáticamente la siguiente versión.
        ultima_version = max(
            (item.version for item in versiones),
            default=0,
        )
        tarifa.version = ultima_version + 1

        # Cerrar la versión anterior cuando comienza una nueva.
        for anterior in versiones:
            if (
                anterior.vigencia_hasta is None
                and anterior.vigencia_desde < tarifa.vigencia_desde
            ):
                anterior.vigencia_hasta = tarifa.vigencia_desde
                anterior.activa = False

        # Comprobar que no existan vigencias superpuestas.
        for anterior in versiones:
            hay_superposicion = (
                tarifa.vigencia_hasta is None
                or anterior.vigencia_desde < tarifa.vigencia_hasta
            ) and (
                anterior.vigencia_hasta is None
                or anterior.vigencia_hasta > tarifa.vigencia_desde
            )

            if hay_superposicion:
                raise ValueError(
                    "La vigencia de la nueva tarifa se superpone "
                    "con una versión existente."
                )

        versiones.append(tarifa)
        return tarifa

    def buscar_por_sede_y_tipo(
        self,
        sede_id,
        tipo_vehiculo,
    ) -> Tarifa | None:
        versiones = self.tarifas.get(
            (sede_id, tipo_vehiculo.strip().upper()),
            [],
        )

        activas = [
            tarifa
            for tarifa in versiones
            if tarifa.activa
        ]

        return max(
            activas,
            key=lambda tarifa: tarifa.version,
            default=None,
        )

    def buscar_vigente(
        self,
        sede_id,
        tipo_vehiculo,
        fecha,
    ) -> Tarifa | None:
        """
        Busca la tarifa que estaba vigente en la fecha indicada.

        No filtra por activa porque una versión histórica puede
        estar inactiva y seguir siendo válida para fechas anteriores.
        """

        versiones = self.tarifas.get(
            (sede_id, tipo_vehiculo.strip().upper()),
            [],
        )

        candidatas = [
            tarifa
            for tarifa in versiones
            if tarifa.vigencia_desde <= fecha
            and (
                tarifa.vigencia_hasta is None
                or tarifa.vigencia_hasta > fecha
            )
        ]

        return max(
            candidatas,
            key=lambda tarifa: tarifa.version,
            default=None,
        )

    def listar_por_sede(self, sede_id):
        return [
            tarifa
            for (id_sede, _), versiones in self.tarifas.items()
            if id_sede == sede_id
            for tarifa in versiones
        ]


def test_configurar_tarifa():
    repositorio = TarifaRepositorioMemoria()
    caso_uso = ConfigurarTarifa(repositorio)
    sede_id = uuid4()

    resultado = caso_uso.ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
    )

    assert resultado.sede_id == sede_id
    assert resultado.tipo_vehiculo == "CARRO"
    assert resultado.tarifa_diurna == Decimal("3000")
    assert resultado.version == 1


def test_configurar_tarifa_moto_gratuita():
    repositorio = TarifaRepositorioMemoria()
    caso_uso = ConfigurarTarifa(repositorio)

    resultado = caso_uso.ejecutar(
        sede_id=uuid4(),
        tipo_vehiculo="MOTO",
        tarifa_diurna=Decimal("0"),
        tarifa_nocturna=Decimal("0"),
    )

    assert resultado.tarifa_diurna == Decimal("0")
    assert resultado.tarifa_nocturna == Decimal("0")


def test_rechazar_configuracion_tarifa_invalida():
    repositorio = TarifaRepositorioMemoria()
    caso_uso = ConfigurarTarifa(repositorio)

    with pytest.raises(ValueError):
        caso_uso.ejecutar(
            sede_id=uuid4(),
            tipo_vehiculo="CARRO",
            tarifa_diurna=Decimal("2000"),
            tarifa_nocturna=Decimal("3000"),
        )


def test_calcular_tarifa_diurna():
    repositorio = TarifaRepositorioMemoria()
    sede_id = uuid4()
    zona = ZoneInfo("America/Bogota")

    ConfigurarTarifa(repositorio).ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
        vigencia_desde=datetime(
            2026, 11, 1, 0, 0,
            tzinfo=zona,
        ),
    )

    caso_uso = CalcularTarifa(repositorio)

    resultado = caso_uso.ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        fecha_hora=datetime(
            2026,
            11,
            23,
            10,
            0,
            tzinfo=zona,
        ),
        zona_horaria="America/Bogota",
    )

    assert resultado["franja_horaria"] == FranjaHoraria.DIURNA.value
    assert resultado["valor_tarifa"] == Decimal("3000")
    assert resultado["version_tarifa"] == 1


def test_calcular_tarifa_nocturna():
    repositorio = TarifaRepositorioMemoria()
    sede_id = uuid4()
    zona = ZoneInfo("America/Bogota")

    ConfigurarTarifa(repositorio).ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
        vigencia_desde=datetime(
            2026, 11, 1, 0, 0,
            tzinfo=zona,
        ),
    )

    caso_uso = CalcularTarifa(repositorio)

    resultado = caso_uso.ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        fecha_hora=datetime(
            2026,
            11,
            23,
            20,
            0,
            tzinfo=zona,
        ),
        zona_horaria="America/Bogota",
    )

    assert resultado["franja_horaria"] == FranjaHoraria.NOCTURNA.value
    assert resultado["valor_tarifa"] == Decimal("2000")
    assert resultado["version_tarifa"] == 1


def test_rechazar_calculo_sin_tarifa_configurada():
    repositorio = TarifaRepositorioMemoria()
    caso_uso = CalcularTarifa(repositorio)
    zona = ZoneInfo("America/Bogota")

    with pytest.raises(ValueError):
        caso_uso.ejecutar(
            sede_id=uuid4(),
            tipo_vehiculo="CARRO",
            fecha_hora=datetime(
                2026,
                11,
                23,
                10,
                0,
                tzinfo=zona,
            ),
            zona_horaria="America/Bogota",
        )


def test_configurar_nueva_version_cierra_anterior():
    repositorio = TarifaRepositorioMemoria()
    sede_id = uuid4()
    zona = ZoneInfo("America/Bogota")

    primera = ConfigurarTarifa(repositorio).ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
        vigencia_desde=datetime(
            2026, 11, 1, 0, 0,
            tzinfo=zona,
        ),
    )

    segunda = ConfigurarTarifa(repositorio).ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("4000"),
        tarifa_nocturna=Decimal("2500"),
        vigencia_desde=datetime(
            2026, 11, 15, 0, 0,
            tzinfo=zona,
        ),
    )

    assert primera.version == 1
    assert segunda.version == 2

    assert primera.activa is False
    assert primera.vigencia_hasta == segunda.vigencia_desde

    assert segunda.activa is True
    assert segunda.vigencia_hasta is None


def test_calcular_tarifa_historica_inactiva():
    repositorio = TarifaRepositorioMemoria()
    sede_id = uuid4()
    zona = ZoneInfo("America/Bogota")

    fecha_inicio = datetime(
        2026, 11, 1, 0, 0,
        tzinfo=zona,
    )

    fecha_fin = datetime(
        2026, 11, 15, 0, 0,
        tzinfo=zona,
    )

    tarifa = Tarifa(
        id=uuid4(),
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
        activa=False,
        version=1,
        vigencia_desde=fecha_inicio,
        vigencia_hasta=fecha_fin,
    )

    repositorio.tarifas[(sede_id, "CARRO")] = [tarifa]

    resultado = CalcularTarifa(repositorio).ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        fecha_hora=datetime(
            2026, 11, 10, 10, 0,
            tzinfo=zona,
        ),
        zona_horaria="America/Bogota",
    )

    assert resultado["tarifa_id"] == tarifa.id
    assert resultado["version_tarifa"] == 1
    assert resultado["valor_tarifa"] == Decimal("3000")


def test_rechazar_calculo_fuera_de_vigencia():
    repositorio = TarifaRepositorioMemoria()
    sede_id = uuid4()
    zona = ZoneInfo("America/Bogota")

    tarifa = Tarifa(
        id=uuid4(),
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
        activa=False,
        version=1,
        vigencia_desde=datetime(
            2026, 11, 1, 0, 0,
            tzinfo=zona,
        ),
        vigencia_hasta=datetime(
            2026, 11, 15, 0, 0,
            tzinfo=zona,
        ),
    )

    repositorio.tarifas[(sede_id, "CARRO")] = [tarifa]

    with pytest.raises(ValueError):
        CalcularTarifa(repositorio).ejecutar(
            sede_id=sede_id,
            tipo_vehiculo="CARRO",
            fecha_hora=datetime(
                2026, 11, 20, 10, 0,
                tzinfo=zona,
            ),
            zona_horaria="America/Bogota",
        )


def test_rechazar_configuracion_con_vigencia_superpuesta():
    repositorio = TarifaRepositorioMemoria()
    sede_id = uuid4()
    zona = ZoneInfo("America/Bogota")

    ConfigurarTarifa(repositorio).ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
        vigencia_desde=datetime(
            2026, 11, 1, 0, 0,
            tzinfo=zona,
        ),
    )

    # Se intenta registrar una tarifa que empieza antes
    # de la vigencia de la versión ya existente.
    with pytest.raises(ValueError):
        ConfigurarTarifa(repositorio).ejecutar(
            sede_id=sede_id,
            tipo_vehiculo="CARRO",
            tarifa_diurna=Decimal("4000"),
            tarifa_nocturna=Decimal("2500"),
            vigencia_desde=datetime(
                2026, 10, 15, 0, 0,
                tzinfo=zona,
            ),
        )
