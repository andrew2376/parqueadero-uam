from decimal import Decimal
from uuid import uuid4

import pytest

from app.modulos.tarifas.dominio.franja_horaria import FranjaHoraria
from app.modulos.tarifas.dominio.tarifa import Tarifa


def crear_tarifa(
    tipo="CARRO",
    diurna="3000",
    nocturna="2000",
):
    return Tarifa(
        id=uuid4(),
        sede_id=uuid4(),
        tipo_vehiculo=tipo,
        tarifa_diurna=Decimal(diurna),
        tarifa_nocturna=Decimal(nocturna),
    )


def test_crear_tarifa_para_carro():
    tarifa = crear_tarifa()

    assert tarifa.tipo_vehiculo == "CARRO"
    assert tarifa.tarifa_diurna == Decimal("3000")
    assert tarifa.tarifa_nocturna == Decimal("2000")


def test_moto_puede_tener_ambas_tarifas_en_cero():
    tarifa = crear_tarifa("MOTO", "0", "0")

    assert tarifa.tarifa_diurna == Decimal("0")
    assert tarifa.tarifa_nocturna == Decimal("0")


def test_moto_puede_tener_tarifas_configuradas():
    tarifa = crear_tarifa("MOTO", "1000", "500")

    assert tarifa.tarifa_diurna == Decimal("1000")
    assert tarifa.tarifa_nocturna == Decimal("500")


def test_rechaza_tarifas_iguales():
    with pytest.raises(ValueError):
        crear_tarifa("CARRO", "2000", "2000")


def test_rechaza_tarifa_nocturna_mayor():
    with pytest.raises(ValueError):
        crear_tarifa("CARRO", "2000", "3000")


def test_rechaza_tarifas_negativas():
    with pytest.raises(ValueError):
        crear_tarifa("CARRO", "-1000", "500")


def test_rechaza_tipo_vehiculo_no_valido():
    with pytest.raises(ValueError):
        crear_tarifa("BICICLETA", "1000", "500")


def test_obtener_tarifa_diurna():
    tarifa = crear_tarifa()

    resultado = tarifa.obtener_valor(FranjaHoraria.DIURNA)

    assert resultado == Decimal("3000")


def test_obtener_tarifa_nocturna():
    tarifa = crear_tarifa()

    resultado = tarifa.obtener_valor(FranjaHoraria.NOCTURNA)

    assert resultado == Decimal("2000")


def test_rechaza_franja_no_valida():
    tarifa = crear_tarifa()

    with pytest.raises(ValueError):
        tarifa.obtener_valor("MADRUGADA")
