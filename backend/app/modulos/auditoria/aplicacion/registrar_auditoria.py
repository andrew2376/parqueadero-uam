from app.modulos.auditoria.dominio.auditoria import Auditoria
from app.modulos.auditoria.dominio.auditoria_repositorio import AuditoriaRepositorio


class RegistrarAuditoria:
    def __init__(self, repositorio: AuditoriaRepositorio):
        self.repositorio = repositorio

    def ejecutar(self, auditoria: Auditoria) -> Auditoria:
        return self.repositorio.registrar(auditoria)
