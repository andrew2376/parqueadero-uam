from uuid import uuid4

import pytest

from app.modulos.reconocimiento_placas.aplicacion.casos_uso_lpr import (
    RegistrarLecturaManual,
    SimularLecturaPlaca,
)
from app.modulos.reconocimiento_placas.dominio.lectura_lpr import (
    EstadoLectura,
    LecturaLPR,
    OrigenLectura,
)
from app.modulos.reconocimiento_placas.infraestructura.lector_lpr_simulado import (
    EscenarioSimulacion,
    LectorLPRSimulado,
)
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class TestReconocimientoPlacasLPR:
    def setup_method(self):
        self.carril_id = uuid4()

    def test_lectura_alta_confianza_carro(self):
        lectura = LecturaLPR(
            carril_id=self.carril_id,
            placa="ABC123",
            confianza=95.0,
            origen=OrigenLectura.AUTOMATICO,
        )
        assert lectura.placa == "ABC123"
        assert lectura.tipo_vehiculo == TipoVehiculo.CARRO
        assert lectura.estado == EstadoLectura.EXITOSA
        assert not lectura.requiere_confirmacion_manual

    def test_lectura_alta_confianza_moto(self):
        lectura = LecturaLPR(
            carril_id=self.carril_id,
            placa="def-45a",
            confianza=88.4,
            origen=OrigenLectura.AUTOMATICO,
        )
        assert lectura.placa == "DEF45A"
        assert lectura.tipo_vehiculo == TipoVehiculo.MOTO
        assert lectura.estado == EstadoLectura.EXITOSA
        assert not lectura.requiere_confirmacion_manual

    def test_lectura_baja_confianza(self):
        lectura = LecturaLPR(
            carril_id=self.carril_id,
            placa="ABC123",
            confianza=55.0,
            origen=OrigenLectura.AUTOMATICO,
        )
        assert lectura.estado == EstadoLectura.BAJA_CONFIANZA
        assert lectura.requiere_confirmacion_manual

    def test_lectura_placa_invalida_es_fallida(self):
        lectura = LecturaLPR(
            carril_id=self.carril_id,
            placa="PLACA_NO_VALIDA",
            confianza=99.0,
            origen=OrigenLectura.AUTOMATICO,
        )
        assert lectura.estado == EstadoLectura.FALLIDA
        assert lectura.tipo_vehiculo is None
        assert lectura.requiere_confirmacion_manual

    def test_confianza_fuera_de_rango_lanza_error(self):
        with pytest.raises(ValueError):
            LecturaLPR(
                carril_id=self.carril_id,
                placa="ABC123",
                confianza=120.0,
            )

    def test_simulador_lpr_con_placa_fija(self):
        simulador = LectorLPRSimulado(placa_fija="XYZ999", confianza_fija=98.0)
        lectura = simulador.capturar_lectura(self.carril_id)

        assert lectura.placa == "XYZ999"
        assert lectura.confianza == 98.0
        assert lectura.tipo_vehiculo == TipoVehiculo.CARRO

    def test_caso_uso_simular_lectura(self):
        simulador = LectorLPRSimulado(placa_fija="MTO12A", confianza_fija=92.5)
        caso_uso = SimularLecturaPlaca(simulador)
        resultado = caso_uso.ejecutar(self.carril_id)

        assert resultado.placa == "MTO12A"
        assert resultado.tipo_vehiculo == TipoVehiculo.MOTO
        assert resultado.estado == EstadoLectura.EXITOSA

    def test_caso_uso_lectura_manual(self):
        caso_manual = RegistrarLecturaManual()
        resultado = caso_manual.ejecutar(self.carril_id, "ABC123")

        assert resultado.origen == OrigenLectura.MANUAL
        assert resultado.confianza == 100.0
        assert resultado.tipo_vehiculo == TipoVehiculo.CARRO

    @pytest.mark.parametrize(
        ("escenario", "placa", "confianza", "estado", "tipo", "requiere_manual"),
        [
            (
                EscenarioSimulacion.ALTA,
                "ABC123",
                95.0,
                EstadoLectura.EXITOSA,
                TipoVehiculo.CARRO,
                False,
            ),
            (
                EscenarioSimulacion.BAJA,
                "DEF45A",
                55.0,
                EstadoLectura.BAJA_CONFIANZA,
                TipoVehiculo.MOTO,
                True,
            ),
            (EscenarioSimulacion.SIN_LECTURA, "", 0.0, EstadoLectura.FALLIDA, None, True),
        ],
    )
    def test_escenarios_reproducibles(
        self, escenario, placa, confianza, estado, tipo, requiere_manual
    ):
        lector = LectorLPRSimulado.para_escenario(escenario)
        lectura = SimularLecturaPlaca(lector).ejecutar(self.carril_id)
        assert lectura.carril_id == self.carril_id
        assert lectura.placa == placa
        assert lectura.confianza == confianza
        assert lectura.estado == estado
        assert lectura.tipo_vehiculo == tipo
        assert lectura.requiere_confirmacion_manual is requiere_manual
