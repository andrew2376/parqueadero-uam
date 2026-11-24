from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.auditoria.aplicacion.consultar_auditoria import ConsultarAuditoria
from app.modulos.auditoria.infraestructura.auditoria_repositorio_sqlalchemy import (
    AuditoriaRepositorioSQLAlchemy,
)
from app.modulos.auditoria.presentacion.esquemas_auditoria import AuditoriaRespuesta
from app.modulos.autenticacion.dominio.usuario import RolUsuario
from app.modulos.autenticacion.presentacion.dependencias_auth import requerir_rol

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoría"],
)


@router.get(
    "",
    response_model=list[AuditoriaRespuesta],
    summary="Consultar registros de auditoría",
)
def consultar_auditorias(
    usuario_id: UUID | None = None,
    accion: str | None = None,
    entidad: str | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    limite: int = Query(default=100, ge=1, le=500),
    sesion: Session = Depends(obtener_sesion),
    usuario_actual=Depends(requerir_rol(RolUsuario.ADMINISTRADOR)),
):
    repositorio = AuditoriaRepositorioSQLAlchemy(sesion)
    caso_uso = ConsultarAuditoria(repositorio)

    return caso_uso.ejecutar(
        usuario_id=usuario_id,
        accion=accion,
        entidad=entidad,
        desde=desde,
        hasta=hasta,
        limite=limite,
    )