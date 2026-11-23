import pytest

from app.modulos.vehiculos.aplicacion.casos_uso_vehiculo import (
    ClasificarPlaca,
    RegistrarVehiculo,
)
from app.modulos.vehiculos.dominio.vehiculo import (
    TipoVehiculo,
    Vehiculo,
    clasificar_placa,
    normalizar_placa,
)


class TestClasificacionPlacas:
    @pytest.mark.parametrize(
        "placa, tipo_esperado",
        [
            ("ABC123", TipoVehiculo.CARRO),
            ("abc123", TipoVehiculo.CARRO),
            (" ABC-123 ", TipoVehiculo.CARRO),
            ("XYZ999", TipoVehiculo.CARRO),
            ("MNO000", TipoVehiculo.CARRO),
        ],
    )
    def test_clasificar_placas_carros(self, placa: str, tipo_esperado: TipoVehiculo):
        assert clasificar_placa(placa) == tipo_esperado

    @pytest.mark.parametrize(
        "placa, tipo_esperado",
        [
            ("ABC12D", TipoVehiculo.MOTO),
            ("abc12d", TipoVehiculo.MOTO),
            (" DEF-45A ", TipoVehiculo.MOTO),
            ("XYZ00Z", TipoVehiculo.MOTO),
        ],
    )
    def test_clasificar_placas_motos(self, placa: str, tipo_esperado: TipoVehiculo):
        assert clasificar_placa(placa) == tipo_esperado

    @pytest.mark.parametrize(
        "placa_invalida",
        [
            "",
            "   ",
            "123ABC",
            "ABCD12",
            "AB1234",
            "A123BC",
            "ABC1234",
            "ABC12",
        ],
    )
    def test_clasificar_placas_invalidas(self, placa_invalida: str):
        with pytest.raises(ValueError):
            clasificar_placa(placa_invalida)

    def test_normalizar_placa(self):
        assert normalizar_placa(" abc-123 ") == "ABC123"
        assert normalizar_placa("xyz 45a") == "XYZ45A"

    def test_creacion_entidad_vehiculo(self):
        vehiculo = Vehiculo.crear_desde_placa("abc123")
        assert vehiculo.placa == "ABC123"
        assert vehiculo.tipo == TipoVehiculo.CARRO

        vehiculo_moto = Vehiculo.crear_desde_placa("xyz45a")
        assert vehiculo_moto.placa == "XYZ45A"
        assert vehiculo_moto.tipo == TipoVehiculo.MOTO

    def test_casos_uso_vehiculo(self):
        caso_clasificar = ClasificarPlaca()
        resultado = caso_clasificar.ejecutar("abc123")
        assert resultado["placa"] == "ABC123"
        assert resultado["tipo"] == "CARRO"

        caso_registrar = RegistrarVehiculo()
        vehiculo = caso_registrar.ejecutar("def45a")
        assert vehiculo.placa == "DEF45A"
        assert vehiculo.tipo == TipoVehiculo.MOTO
