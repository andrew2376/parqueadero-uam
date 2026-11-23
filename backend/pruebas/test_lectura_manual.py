from uuid import uuid4
import pytest

from app.modulos.reconocimiento_placas.aplicacion.casos_uso_lpr import (
    ValidarLecturaBajaConfianza,
)
from app.modulos.reconocimiento_placas.dominio.lectura_lpr import (
    EstadoLectura,
    LecturaLPR,
    OrigenLectura,
)
from app.modulos.reconocimiento_placas.presentacion.esquemas_lpr import (
    ValidarLecturaManualSolicitud,
)
from app.modulos.reconocimiento_placas.presentacion.lpr_router import (
    validar_lectura_manual,
)
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


def test_lectura_automatica_detecta_baja_confianza_segun_umbral():
    carril_id = uuid4()
    # Confianza del 65% es menor al umbral por defecto (70.0%)
    lectura = LecturaLPR(
        carril_id=carril_id,
        placa="ABC123",
        confianza=65.0,
        origen=OrigenLectura.AUTOMATICO,
    )

    assert lectura.estado == EstadoLectura.BAJA_CONFIANZA
    assert lectura.requiere_confirmacion_manual is True
    assert lectura.tipo_vehiculo == TipoVehiculo.CARRO


def test_lectura_automatica_exitosa_supera_umbral():
    carril_id = uuid4()
    lectura = LecturaLPR(
        carril_id=carril_id,
        placa="ABC123",
        confianza=85.0,
        origen=OrigenLectura.AUTOMATICO,
    )

    assert lectura.estado == EstadoLectura.EXITOSA
    assert lectura.requiere_confirmacion_manual is False


def test_confirmar_por_operador_corrige_placa_y_establece_confianza_maxima():
    carril_id = uuid4()
    caso_uso = ValidarLecturaBajaConfianza()

    # La cámara detectó erróneamente 'ABO123' con baja confianza (45%)
    # El operador confirma y corrige a 'ABC123'
    resultado = caso_uso.ejecutar(
        carril_id=carril_id,
        placa_confirmada="ABC123",
        operador_id="usr-operador-01",
        placa_detectada_previa="ABO123",
        confianza_previa=45.0,
    )

    assert resultado.placa == "ABC123"
    assert resultado.placa_original_detectada == "ABO123"
    assert resultado.confianza == 100.0
    assert resultado.origen == OrigenLectura.CONFIRMADA_OPERADOR
    assert resultado.estado == EstadoLectura.EXITOSA
    assert resultado.operador_id == "usr-operador-01"
    assert resultado.tipo_vehiculo == TipoVehiculo.CARRO
    assert resultado.requiere_confirmacion_manual is False


def test_confirmar_lectura_moto_colombiana():
    carril_id = uuid4()
    caso_uso = ValidarLecturaBajaConfianza()

    resultado = caso_uso.ejecutar(
        carril_id=carril_id,
        placa_confirmada="XYZ89A",
        operador_id="usr-operador-02",
        confianza_previa=55.0,
    )

    assert resultado.placa == "XYZ89A"
    assert resultado.tipo_vehiculo == TipoVehiculo.MOTO
    assert resultado.confianza == 100.0


def test_rechaza_placa_invalida_en_validacion_manual():
    carril_id = uuid4()
    caso_uso = ValidarLecturaBajaConfianza()

    with pytest.raises(ValueError):
        caso_uso.ejecutar(
            carril_id=carril_id,
            placa_confirmada="INVALIDA",
            operador_id="usr-operador-01",
        )


def test_endpoint_validar_lectura_manual_router():
    carril_id = uuid4()
    solicitud = ValidarLecturaManualSolicitud(
        carril_id=carril_id,
        placa_confirmada="KLR65A",
        operador_id="operador_principal",
        placa_detectada_previa="KLR650",
        confianza_previa=58.0,
        umbral_confianza=70.0,
    )

    datos = validar_lectura_manual(solicitud)

    assert datos.placa == "KLR65A"
    assert datos.placa_original_detectada == "KLR650"
    assert datos.confianza == 100.0
    assert datos.origen == OrigenLectura.CONFIRMADA_OPERADOR
    assert datos.tipo_vehiculo == TipoVehiculo.MOTO
    assert datos.requiere_confirmacion_manual is False
