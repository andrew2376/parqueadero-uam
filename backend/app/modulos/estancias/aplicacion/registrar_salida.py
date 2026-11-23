from datetime import datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo
from app.modulos.estancias.dominio.estancia_repositorio import EstanciaRepositorio
from app.modulos.pagos.infraestructura.pago_modelo import PagoModelo
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo
from app.modulos.vehiculos.dominio.vehiculo import normalizar_placa


class RegistrarSalida:
    def __init__(self, repositorio: EstanciaRepositorio, sesion):
        self.repositorio = repositorio
        self.sesion = sesion

    def ejecutar(self, placa: str, sede_id: UUID) -> dict:

        placa_normalizada = normalizar_placa(placa)

        # 1. Buscar estancia activa
        estancia = self.repositorio.buscar_activa_por_placa(
            placa_normalizada,
            sede_id,
        )

        if estancia is None:
            return {
                "autorizado": False,
                "decision_barrera": "DENEGAR",
                "placa": placa_normalizada,
                "sede_id": sede_id,
                "motivo": "No existe una estancia activa para este vehículo.",
            }

        # 2. Consultar sede y calcular día operativo
        sede = self.sesion.get(SedeModelo, sede_id)

        if sede is None:
            return {
                "autorizado": False,
                "decision_barrera": "DENEGAR",
                "placa": placa_normalizada,
                "sede_id": sede_id,
                "motivo": "La sede no existe.",
            }

        zona_horaria = ZoneInfo(sede.zona_horaria)
        ahora = datetime.now(zona_horaria)

        inicio_dia = ahora.replace(
            hour=sede.inicio_dia_operativo.hour,
            minute=sede.inicio_dia_operativo.minute,
            second=sede.inicio_dia_operativo.second,
            microsecond=0,
        )

        if ahora < inicio_dia:
            dia_operativo = ahora.date() - timedelta(days=1)
        else:
            dia_operativo = ahora.date()

        # 3. Buscar cobro del día operativo
        cobro = (
            self.sesion.query(CobroModelo)
            .filter(
                CobroModelo.placa == placa_normalizada,
                CobroModelo.sede_id == sede_id,
                CobroModelo.dia_operativo == dia_operativo,
            )
            .first()
        )

        if cobro is None:
            return {
                "autorizado": False,
                "decision_barrera": "DENEGAR",
                "placa": placa_normalizada,
                "sede_id": sede_id,
                "dia_operativo": dia_operativo,
                "motivo": "No existe un cobro vigente para este vehículo.",
            }

        # 4. Verificar pago
        pago = self.sesion.query(PagoModelo).filter(PagoModelo.cobro_id == cobro.id).first()

        if pago is None:
            return {
                "autorizado": False,
                "decision_barrera": "DENEGAR",
                "placa": placa_normalizada,
                "sede_id": sede_id,
                "dia_operativo": dia_operativo,
                "cobro_id": cobro.id,
                "motivo": "El cobro del día operativo está pendiente de pago.",
            }

        # 5. Registrar salida de la estancia
        salida_registrada = self.repositorio.registrar_salida(
            estancia.id,
            ahora,
        )

        if not salida_registrada:
            return {
                "autorizado": False,
                "decision_barrera": "DENEGAR",
                "placa": placa_normalizada,
                "sede_id": sede_id,
                "dia_operativo": dia_operativo,
                "cobro_id": cobro.id,
                "motivo": "La estancia ya fue cerrada o no pudo registrarse la salida.",
            }

        # 6. Autorizar barrera
        return {
            "autorizado": True,
            "decision_barrera": "AUTORIZAR",
            "placa": placa_normalizada,
            "sede_id": sede_id,
            "dia_operativo": dia_operativo,
            "cobro_id": cobro.id,
            "estancia_id": estancia.id,
            "fecha_hora_salida": ahora,
            "motivo": "Salida autorizada. Cobro pagado y estancia cerrada.",
        }
