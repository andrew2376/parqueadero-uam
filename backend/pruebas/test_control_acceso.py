from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modulos.accesos.presentacion.esquemas_ingreso import RegistrarIngresoEsquema
from app.modulos.accesos.presentacion.ingreso_router import registrar_ingreso
from app.modulos.carriles.dominio.carril import TipoCarril


@pytest.mark.parametrize("problema", ["direccion", "inactivo", "otra_sede", "inexistente"])
def test_rechaza_carril_incompatible_antes_de_registrar_ingreso(problema):
    sede_id = uuid4()
    carril_id = uuid4()
    datos = RegistrarIngresoEsquema(sede_id=sede_id, carril_id=carril_id, placa="ABC123")
    sesion = MagicMock()
    sesion.get.return_value = None
    if problema != "inexistente":
        sesion.get.return_value = SimpleNamespace(
            sede_id=uuid4() if problema == "otra_sede" else sede_id,
            activo=problema != "inactivo",
            tipo=TipoCarril.SALIDA if problema == "direccion" else TipoCarril.MIXTO,
        )

    with pytest.raises(HTTPException) as error:
        registrar_ingreso(datos, sesion, MagicMock())

    assert error.value.status_code == 422
    sesion.commit.assert_not_called()
