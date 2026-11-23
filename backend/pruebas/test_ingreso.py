from datetime import time
from uuid import uuid4

from app.modulos.accesos.aplicacion.registrar_ingreso import RegistrarIngresoVehiculo
from app.modulos.accesos.dominio.acceso_repositorio import AccesoRepositorio
from app.modulos.accesos.dominio.ingreso import (
    DecisionBarrera,
    EstadoAcceso,
    RegistroIngreso,
)
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class AccesoRepositorioEnMemoria(AccesoRepositorio):

    def __init__(self):
        self.ingresos: list[RegistroIngreso] = []

    def guardar_ingreso(self, ingreso: RegistroIngreso) -> RegistroIngreso:
        self.ingresos.append(ingreso)
        return ingreso

    def buscar_ingreso_activo_por_placa(self, placa: str, sede_id) -> RegistroIngreso | None:
        for ing in self.ingresos:
            if ing.placa == placa and ing.sede_id == sede_id and ing.estado == EstadoAcceso.ACTIVO:
                return ing
        return None

    def contar_vehiculos_activos(self, sede_id, tipo_vehiculo: TipoVehiculo) -> int:
        return sum(
            1
            for ing in self.ingresos
            if ing.sede_id == sede_id and ing.tipo_vehiculo == tipo_vehiculo and ing.estado == EstadoAcceso.ACTIVO
        )


class MockSession:
    """Mock mínimo de SQLAlchemy Session para pruebas unitarias de ingreso."""

    def __init__(self, sede: SedeModelo):
        self.sede = sede

    def get(self, entity_class, entity_id):
        if entity_class == SedeModelo and entity_id == self.sede.id:
            return self.sede
        return None

    def query(self, *args, **kwargs):
        class MockQuery:
            def filter(self, *f_args, **f_kwargs):
                return self
            def first(self):
                return None
        return MockQuery()


class TestCasoUsoIngreso:

    def setup_method(self):
        self.sede_id = uuid4()
        self.carril_id = uuid4()
        self.sede = SedeModelo(
            id=self.sede_id,
            nombre="Sede Principal UAM",
            cupos_carro=2,
            cupos_moto=2,
            inicio_dia_operativo=time(6, 0),
            zona_horaria="America/Bogota",
        )
        self.repositorio = AccesoRepositorioEnMemoria()
        self.sesion = MockSession(self.sede)
        self.caso_ingreso = RegistrarIngresoVehiculo(
            repositorio=self.repositorio,
            sesion=self.sesion,
        )

    def test_ingreso_exitoso_carro(self):
        resultado = self.caso_ingreso.ejecutar(
            sede_id=self.sede_id,
            carril_id=self.carril_id,
            placa_raw="ABC123",
        )
        assert resultado.autorizado is True
        assert resultado.decision_barrera == DecisionBarrera.ABRIR
        assert resultado.tipo_vehiculo == TipoVehiculo.CARRO
        assert resultado.cupos_disponibles_restantes == 1
        assert resultado.acceso_id is not None

    def test_ingreso_exitoso_moto(self):
        resultado = self.caso_ingreso.ejecutar(
            sede_id=self.sede_id,
            carril_id=self.carril_id,
            placa_raw="def-45a",
        )
        assert resultado.autorizado is True
        assert resultado.decision_barrera == DecisionBarrera.ABRIR
        assert resultado.tipo_vehiculo == TipoVehiculo.MOTO
        assert resultado.cupos_disponibles_restantes == 1

    def test_anti_passback_rechaza_vehiculo_ya_dentro(self):
        # Primer ingreso
        self.caso_ingreso.ejecutar(
            sede_id=self.sede_id,
            carril_id=self.carril_id,
            placa_raw="ABC123",
        )
        # Segundo ingreso con la misma placa sin haber salido
        segundo = self.caso_ingreso.ejecutar(
            sede_id=self.sede_id,
            carril_id=self.carril_id,
            placa_raw="ABC123",
        )
        assert segundo.autorizado is False
        assert segundo.decision_barrera == DecisionBarrera.MANTENER_CERRADA
        assert "Anti-passback" in segundo.mensaje

    def test_cupos_agotados_bloquea_ingreso(self):
        # Llenar los 2 cupos de carro
        self.caso_ingreso.ejecutar(self.sede_id, self.carril_id, "ABC123")
        self.caso_ingreso.ejecutar(self.sede_id, self.carril_id, "XYZ789")

        # Tercer carro debe ser rechazado
        tercero = self.caso_ingreso.ejecutar(self.sede_id, self.carril_id, "UAM100")
        assert tercero.autorizado is False
        assert tercero.decision_barrera == DecisionBarrera.MANTENER_CERRADA
        assert "Parqueadero lleno" in tercero.mensaje

    def test_placa_invalida_rechaza_ingreso(self):
        resultado = self.caso_ingreso.ejecutar(
            sede_id=self.sede_id,
            carril_id=self.carril_id,
            placa_raw="PLACA_MALA",
        )
        assert resultado.autorizado is False
        assert resultado.decision_barrera == DecisionBarrera.MANTENER_CERRADA
