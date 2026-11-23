
from app.modulos.carriles.dominio.carril_repositorio import (
    CarrilRepositorio,
)
from app.modulos.eventos_lectura.aplicacion.registrar_evento_lectura import (
    RegistrarEventoLectura,
)
from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EventoLectura,
    EstadoEventoLectura,
    OrigenEventoLectura,
)
from app.modulos.reconocimiento_placas.dominio.lectura_lpr import (
    LecturaLPR,
)


class RegistrarEventoDesdeLPR:
    """
    Coordina el resultado del reconocimiento de placas
    con el registro de eventos de lectura.
    """

    def __init__(
        self,
        carriles: CarrilRepositorio,
        registrar_evento: RegistrarEventoLectura,
    ) -> None:
        self.carriles = carriles
        self.registrar_evento = registrar_evento

    def ejecutar(self, lectura: LecturaLPR) -> EventoLectura:
        carril = self.carriles.obtener_por_id(lectura.carril_id)

        if carril is None:
            raise ValueError("El carril indicado no existe.")

        evento = EventoLectura(
            sede_id=carril.sede_id,
            carril_id=lectura.carril_id,
            placa=lectura.placa or None,
            confianza=lectura.confianza,
            origen=OrigenEventoLectura(lectura.origen.value),
            estado=EstadoEventoLectura(lectura.estado.value),
            fecha_hora=lectura.creado_en,
        )

        return self.registrar_evento.ejecutar(evento)
