from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modulos.reconocimiento_placas.presentacion.esquemas_lpr import (
    LecturaManualSolicitud,
    ValidarLecturaManualSolicitud,
)

ESQUEMAS = [
    (LecturaManualSolicitud, "placa"),
    (ValidarLecturaManualSolicitud, "placa_confirmada"),
]


@pytest.mark.parametrize(("esquema", "campo"), ESQUEMAS)
@pytest.mark.parametrize(
    ("placa", "normalizada"),
    [
        (" abc-123 ", "ABC123"),
        ("xYz 789", "XYZ789"),
        (" klr-65a ", "KLR65A"),
        ("dEf 45b", "DEF45B"),
    ],
)
def test_normaliza_placa_antes_de_validar_longitud(esquema, campo, placa, normalizada):
    datos = esquema(carril_id=uuid4(), operador_id="operador-prueba", **{campo: placa})

    assert getattr(datos, campo) == normalizada


@pytest.mark.parametrize(("esquema", "campo"), ESQUEMAS)
@pytest.mark.parametrize(
    ("placa", "error"),
    [
        ("", "string_too_short"),
        (" - - ", "string_too_short"),
        (" ab-12 ", "string_too_short"),
        (" abcd-123 ", "string_too_long"),
        (123456, "string_type"),
        (None, "string_type"),
    ],
)
def test_rechaza_placas_invalidas_segun_el_esquema(esquema, campo, placa, error):
    with pytest.raises(ValidationError) as exc:
        esquema(carril_id=uuid4(), operador_id="operador-prueba", **{campo: placa})

    errores = exc.value.errors()
    assert len(errores) == 1
    assert (errores[0]["loc"], errores[0]["type"]) == ((campo,), error)
