from uuid import UUID

from sqlalchemy.orm import Session

from app.modulos.accesos.aplicacion.validar_reingreso import ValidarReingreso
from app.modulos.accesos.dominio.acceso_repositorio import AccesoRepositorio
from app.modulos.accesos.dominio.ingreso import (
    DecisionBarrera,
    RegistroIngreso,
    ResultadoIngreso,
)
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo
from app.modulos.vehiculos.dominio.vehiculo import (
    TipoVehiculo,
    clasificar_placa,
    normalizar_placa,
)


class RegistrarIngresoVehiculo:
    """
    Caso de uso S113:
    1. Normaliza y clasifica la placa (F-02 / RN-01).
    2. Valida anti-passback (que el vehículo no esté ya adentro).
    3. Valida reingreso con pase pagado del día (RN-05).
    4. Valida disponibilidad de cupos por tipo de vehículo (RN-06).
    5. Registra el ingreso y emite decisión de barrera (ABRIR / MANTENER_CERRADA).
    """

    def __init__(self, repositorio: AccesoRepositorio, sesion: Session):
        self.repositorio = repositorio
        self.sesion = sesion
        self.validador_reingreso = ValidarReingreso(sesion)

    def ejecutar(self, sede_id: UUID, carril_id: UUID, placa_raw: str) -> ResultadoIngreso:
        placa = normalizar_placa(placa_raw)

        # 1. Validar y clasificar formato de placa
        try:
            tipo_vehiculo = clasificar_placa(placa)
        except ValueError as e:
            return ResultadoIngreso(
                autorizado=False,
                decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                mensaje=str(e),
                placa=placa or placa_raw,
            )

        # 2. Consultar sede y cupos totales
        sede = self.sesion.get(SedeModelo, sede_id)
        if sede is None:
            return ResultadoIngreso(
                autorizado=False,
                decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                mensaje="La sede especificada no existe.",
                placa=placa,
                tipo_vehiculo=tipo_vehiculo,
            )

        # 3. Validar Anti-Passback: el vehículo no puede ingresar si ya está adentro
        activo = self.repositorio.buscar_ingreso_activo_por_placa(placa=placa, sede_id=sede_id)
        if activo is not None:
            return ResultadoIngreso(
                autorizado=False,
                decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                mensaje=f"Anti-passback: El vehículo con placa {placa} ya registra un ingreso activo en esta sede.",
                placa=placa,
                tipo_vehiculo=tipo_vehiculo,
            )

        # 4. Validar si es un reingreso con pase pagado
        reingreso_info = self.validador_reingreso.ejecutar(placa=placa, sede_id=sede_id)
        es_reingreso = reingreso_info.get("autorizado", False)

        # 5. Validar cupos por tipo de vehículo
        cupos_maximos = sede.cupos_carro if tipo_vehiculo == TipoVehiculo.CARRO else sede.cupos_moto
        ocupados = self.repositorio.contar_vehiculos_activos(
            sede_id=sede_id, tipo_vehiculo=tipo_vehiculo
        )
        disponibles = cupos_maximos - ocupados

        if disponibles <= 0 and not es_reingreso:
            return ResultadoIngreso(
                autorizado=False,
                decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                mensaje=f"Parqueadero lleno para {tipo_vehiculo.value.lower()}s. Cupos disponibles: 0.",
                placa=placa,
                tipo_vehiculo=tipo_vehiculo,
                es_reingreso=False,
                cupos_disponibles_restantes=0,
            )

        # 6. Registrar ingreso exitoso
        nuevo_ingreso = RegistroIngreso(
            sede_id=sede_id,
            carril_id=carril_id,
            placa=placa,
            tipo_vehiculo=tipo_vehiculo,
            es_reingreso=es_reingreso,
        )
        self.repositorio.guardar_ingreso(nuevo_ingreso)

        # Cupos restantes tras el ingreso
        cupos_restantes = max(0, disponibles - (0 if es_reingreso else 1))
        mensaje_exito = (
            f"Reingreso autorizado para {placa} ({tipo_vehiculo.value}). Pase del día vigente."
            if es_reingreso
            else f"Ingreso autorizado para {placa} ({tipo_vehiculo.value}). Barrera abierta."
        )

        return ResultadoIngreso(
            autorizado=True,
            decision_barrera=DecisionBarrera.ABRIR,
            mensaje=mensaje_exito,
            placa=placa,
            tipo_vehiculo=tipo_vehiculo,
            es_reingreso=es_reingreso,
            cupos_disponibles_restantes=cupos_restantes,
            acceso_id=nuevo_ingreso.id,
        )
