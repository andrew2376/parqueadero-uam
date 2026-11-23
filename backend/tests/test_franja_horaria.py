from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from app.modulos.tarifas.dominio.franja_horaria import (
    FranjaHoraria,
    calcular_dia_operativo,
    determinar_franja_horaria,
)

ZONA = "America/Bogota"


@pytest.mark.parametrize(
    ("hora", "franja"),
    [
        (5, FranjaHoraria.NOCTURNA),
        (6, FranjaHoraria.DIURNA),
        (17, FranjaHoraria.DIURNA),
        (18, FranjaHoraria.NOCTURNA),
        (23, FranjaHoraria.NOCTURNA),
    ],
)
def test_determinar_franja_horaria(hora, franja):
    fecha = datetime(
        2026,
        11,
        23,
        hora,
        0,
        tzinfo=ZoneInfo(ZONA),
    )

    resultado = determinar_franja_horaria(fecha, ZONA)

    assert resultado == franja


@pytest.mark.parametrize(
    ("fecha_hora", "dia_esperado"),
    [
        (
            datetime(2026, 11, 23, 5, 59, tzinfo=ZoneInfo(ZONA)),
            datetime(2026, 11, 22).date(),
        ),
        (
            datetime(2026, 11, 23, 6, 0, tzinfo=ZoneInfo(ZONA)),
            datetime(2026, 11, 23).date(),
        ),
        (
            datetime(2026, 11, 23, 18, 0, tzinfo=ZoneInfo(ZONA)),
            datetime(2026, 11, 23).date(),
        ),
        (
            datetime(2026, 11, 24, 2, 0, tzinfo=ZoneInfo(ZONA)),
            datetime(2026, 11, 23).date(),
        ),
    ],
)
def test_calcular_dia_operativo(fecha_hora, dia_esperado):
    resultado = calcular_dia_operativo(
        fecha_hora,
        ZONA,
        time(6, 0),
    )

    assert resultado == dia_esperado


def test_rechaza_fecha_sin_zona_horaria():
    fecha = datetime(2026, 11, 23, 5, 0)

    with pytest.raises(ValueError):
        determinar_franja_horaria(fecha, ZONA)
