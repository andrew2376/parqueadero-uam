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
        self.tarifas[clave] = tarifa
        return tarifa

    def buscar_por_sede_y_tipo(
        self,
        sede_id,
        tipo_vehiculo,
    ) -> Tarifa | None:
        return self.tarifas.get((sede_id, tipo_vehiculo.strip().upper()))

    def listar_por_sede(self, sede_id):
        return [tarifa for (id_sede, _), tarifa in self.tarifas.items() if id_sede == sede_id]


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

    ConfigurarTarifa(repositorio).ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
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
            tzinfo=ZoneInfo("America/Bogota"),
        ),
        zona_horaria="America/Bogota",
    )

    assert resultado["franja_horaria"] == FranjaHoraria.DIURNA.value
    assert resultado["valor_tarifa"] == Decimal("3000")


def test_calcular_tarifa_nocturna():
    repositorio = TarifaRepositorioMemoria()
    sede_id = uuid4()

    ConfigurarTarifa(repositorio).ejecutar(
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
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
            tzinfo=ZoneInfo("America/Bogota"),
        ),
        zona_horaria="America/Bogota",
    )

    assert resultado["franja_horaria"] == FranjaHoraria.NOCTURNA.value
    assert resultado["valor_tarifa"] == Decimal("2000")


def test_rechazar_calculo_sin_tarifa_configurada():
    repositorio = TarifaRepositorioMemoria()
    caso_uso = CalcularTarifa(repositorio)

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
                tzinfo=ZoneInfo("America/Bogota"),
            ),
            zona_horaria="America/Bogota",
        )


def test_rechazar_calculo_con_tarifa_inactiva():
    repositorio = TarifaRepositorioMemoria()
    sede_id = uuid4()

    tarifa = Tarifa(
        id=uuid4(),
        sede_id=sede_id,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("3000"),
        tarifa_nocturna=Decimal("2000"),
        activa=False,
    )

    repositorio.guardar(tarifa)

    caso_uso = CalcularTarifa(repositorio)

    with pytest.raises(ValueError):
        caso_uso.ejecutar(
            sede_id=sede_id,
            tipo_vehiculo="CARRO",
            fecha_hora=datetime(
                2026,
                11,
                23,
                10,
                0,
                tzinfo=ZoneInfo("America/Bogota"),
            ),
            zona_horaria="America/Bogota",
        )
