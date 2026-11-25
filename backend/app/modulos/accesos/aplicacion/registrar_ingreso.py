from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.modulos.accesos.aplicacion.validar_reingreso import ValidarReingreso
from app.modulos.accesos.dominio.acceso_repositorio import AccesoRepositorio
from app.modulos.accesos.dominio.ingreso import (
    DecisionBarrera,
    RegistroIngreso,
    ResultadoIngreso,
)
from app.modulos.carriles.dominio.carril import TipoCarril
from app.modulos.carriles.infraestructura.carril_modelo import CarrilModelo
from app.modulos.cobros.aplicacion.generar_cobro import GenerarCobro
from app.modulos.estancias.infraestructura.estancia_modelo import EstanciaModelo
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo
from app.modulos.tarifas.dominio.franja_horaria import calcular_dia_operativo
from app.modulos.vehiculos.dominio.vehiculo import (
    TipoVehiculo,
    clasificar_placa,
    normalizar_placa,
)


class RegistrarIngresoVehiculo:
    """
    Caso de uso S113 integrado con S202 y S206.

    1. Normaliza y clasifica la placa.
    2. Valida anti-passback.
    3. Valida reingreso con pase pagado del día.
    4. Bloquea la sede para controlar ingresos concurrentes.
    5. Valida la disponibilidad por tipo de vehículo.
    6. Genera o recupera el cobro del día operativo.
    7. Registra la estancia en PostgreSQL.
    8. Emite la decisión de barrera.
    """

    def __init__(
        self,
        repositorio: AccesoRepositorio,
        sesion: Session,
    ):
        self.repositorio = repositorio
        self.sesion = sesion
        self.validador_reingreso = ValidarReingreso(sesion)

    def ejecutar(
        self,
        sede_id: UUID,
        carril_id: UUID,
        placa_raw: str,
    ) -> ResultadoIngreso:

        placa = normalizar_placa(placa_raw)

        # 1. Clasificar la placa.
        try:
            tipo_vehiculo = clasificar_placa(placa)
        except ValueError as e:
            return ResultadoIngreso(
                autorizado=False,
                decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                mensaje=str(e),
                placa=placa or placa_raw,
            )

        try:
            # 2. Validar que la sede exista.
            sede = self.sesion.get(SedeModelo, sede_id)

            if sede is None:
                return ResultadoIngreso(
                    autorizado=False,
                    decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                    mensaje="La sede especificada no existe.",
                    placa=placa,
                    tipo_vehiculo=tipo_vehiculo,
                )

            # 3. Validar anti-passback del repositorio de accesos.
            activo = self.repositorio.buscar_ingreso_activo_por_placa(
                placa=placa,
                sede_id=sede_id,
            )

            if activo is not None:
                return ResultadoIngreso(
                    autorizado=False,
                    decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                    mensaje=(
                        f"Anti-passback: El vehículo con placa {placa} "
                        "ya registra un ingreso activo en esta sede."
                    ),
                    placa=placa,
                    tipo_vehiculo=tipo_vehiculo,
                )

            # 4. Validar reingreso autorizado.
            reingreso_info = self.validador_reingreso.ejecutar(
                placa=placa,
                sede_id=sede_id,
            )
            es_reingreso = reingreso_info.get("autorizado", False)

            # 5. Bloquear la fila de la sede.
            # El bloqueo permanece hasta el commit o rollback.
            sede_bloqueada = (
                self.sesion.query(SedeModelo)
                .filter(SedeModelo.id == sede_id)
                .with_for_update()
                .first()
            )

            if sede_bloqueada is None:
                self.sesion.rollback()

                return ResultadoIngreso(
                    autorizado=False,
                    decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                    mensaje="La sede especificada no existe.",
                    placa=placa,
                    tipo_vehiculo=tipo_vehiculo,
                )

            carril = self.sesion.get(CarrilModelo, carril_id, with_for_update=True)
            if carril is None or carril.sede_id != sede_id:
                raise ValueError("El carril no pertenece a la sede indicada.")
            if not carril.activo or carril.tipo not in (TipoCarril.ENTRADA, TipoCarril.MIXTO):
                raise ValueError("El carril no está habilitado para ingreso.")

            # 6. Comprobar anti-passback contra las estancias reales.
            estancia_activa = (
                self.sesion.query(EstanciaModelo)
                .filter(
                    EstanciaModelo.sede_id == sede_id,
                    EstanciaModelo.placa == placa,
                    EstanciaModelo.estado == "DENTRO",
                    EstanciaModelo.fecha_hora_salida.is_(None),
                )
                .first()
            )

            if estancia_activa is not None:
                self.sesion.rollback()

                return ResultadoIngreso(
                    autorizado=False,
                    decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                    mensaje=(
                        f"Anti-passback: El vehículo con placa {placa} "
                        "ya registra una estancia activa en esta sede."
                    ),
                    placa=placa,
                    tipo_vehiculo=tipo_vehiculo,
                )

            # 7. Consultar capacidad y ocupación real.
            cupos_maximos = (
                sede_bloqueada.cupos_carro
                if tipo_vehiculo == TipoVehiculo.CARRO
                else sede_bloqueada.cupos_moto
            )

            ocupados = (
                self.sesion.query(EstanciaModelo)
                .filter(
                    EstanciaModelo.sede_id == sede_id,
                    EstanciaModelo.tipo_vehiculo == tipo_vehiculo.value,
                    EstanciaModelo.estado == "DENTRO",
                    EstanciaModelo.fecha_hora_salida.is_(None),
                )
                .count()
            )

            disponibles = max(0, cupos_maximos - ocupados)

            # El reingreso autorizado conserva la excepción de S113.
            if disponibles <= 0 and not es_reingreso:
                self.sesion.rollback()

                return ResultadoIngreso(
                    autorizado=False,
                    decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                    mensaje=(
                        f"Parqueadero lleno para "
                        f"{tipo_vehiculo.value.lower()}s. "
                        "Cupos disponibles: 0."
                    ),
                    placa=placa,
                    tipo_vehiculo=tipo_vehiculo,
                    es_reingreso=False,
                    cupos_disponibles_restantes=0,
                )

            # 8. Obtener la hora local y el día operativo de la sede.
            ahora = datetime.now(ZoneInfo(sede_bloqueada.zona_horaria))

            dia_operativo = calcular_dia_operativo(
                fecha_hora=ahora,
                zona_horaria=sede_bloqueada.zona_horaria,
                inicio_dia_operativo=sede_bloqueada.inicio_dia_operativo,
            )

            # 9. Generar el primer cobro del día o recuperar el existente.
            # El cobro conserva la tarifa y versión originales durante
            # todos los reingresos del mismo día operativo.
            GenerarCobro(self.sesion).ejecutar(
                placa=placa,
                sede_id=sede_id,
                tipo_vehiculo=tipo_vehiculo.value,
                dia_operativo=dia_operativo,
                fecha_hora=ahora,
                zona_horaria=sede_bloqueada.zona_horaria,
            )

            # 10. Crear la estancia que contabiliza S202.
            # Se reutiliza la misma hora local calculada para el cobro.
            nueva_estancia = EstanciaModelo(
                sede_id=sede_id,
                placa=placa,
                tipo_vehiculo=tipo_vehiculo.value,
                fecha_hora_entrada=ahora,
                fecha_hora_salida=None,
                estado="DENTRO",
            )

            self.sesion.add(nueva_estancia)
            self.sesion.flush()

            # 11. Calcular cupos restantes después del ingreso.
            ocupados += 1
            cupos_restantes = max(0, cupos_maximos - ocupados)

            # 12. Confirmar cobro y estancia en la misma transacción.
            self.sesion.commit()

            # 13. Registrar el acceso conservando S113.
            nuevo_ingreso = RegistroIngreso(
                sede_id=sede_id,
                carril_id=carril_id,
                placa=placa,
                tipo_vehiculo=tipo_vehiculo,
                es_reingreso=es_reingreso,
            )

            self.repositorio.guardar_ingreso(nuevo_ingreso)

            mensaje_exito = (
                f"Reingreso autorizado para {placa} ({tipo_vehiculo.value}). Pase del día vigente."
                if es_reingreso
                else (f"Ingreso autorizado para {placa} ({tipo_vehiculo.value}). Barrera abierta.")
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

        except ValueError as e:
            self.sesion.rollback()

            return ResultadoIngreso(
                autorizado=False,
                decision_barrera=DecisionBarrera.MANTENER_CERRADA,
                mensaje=str(e),
                placa=placa,
                tipo_vehiculo=tipo_vehiculo,
                es_reingreso=False,
                cupos_disponibles_restantes=0,
            )

        except Exception:
            self.sesion.rollback()
            raise
