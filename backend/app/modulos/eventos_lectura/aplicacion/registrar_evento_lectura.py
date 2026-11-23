from app.modulos.carriles.dominio.carril_repositorio import CarrilRepositorio
from app.modulos.eventos_lectura.dominio.evento_lectura import EventoLectura
from app.modulos.eventos_lectura.dominio.evento_lectura_repositorio import (
    EventoLecturaRepositorio,
)


class RegistrarEventoLectura:
    """
    Caso de uso encargado de registrar un evento de lectura
    y verificar su relación con la sede y el carril.
    """

    def __init__(
        self,
        eventos: EventoLecturaRepositorio,
        carriles: CarrilRepositorio,
    ) -> None:
        self.eventos = eventos
        self.carriles = carriles

    def ejecutar(self, evento: EventoLectura) -> EventoLectura:
        carril = self.carriles.obtener_por_id(evento.carril_id)

        if carril is None:
            raise ValueError("El carril indicado no existe.")

        if carril.sede_id != evento.sede_id:
            raise ValueError("El carril indicado no pertenece a la sede especificada.")

        return self.eventos.guardar(evento)
