import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.estancias.infraestructura.estancia_modelo import EstanciaModelo
from app.modulos.eventos_lectura.infraestructura.evento_lectura_modelo import (
    EventoLecturaModelo,
)
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo

router = APIRouter(
    prefix="/panel",
    tags=["Panel Operador"],
)


class ActividadRecienteItem(BaseModel):
    tipo: str  # "INGRESO" | "SALIDA" | "LECTURA"
    placa: str
    hora: str
    estado: str


class VehiculoActivoItem(BaseModel):
    placa: str
    tipo_vehiculo: str
    ingreso: str
    estado: str


class MetricasPanelRespuesta(BaseModel):
    sede_id: str
    sede_nombre: str
    vehiculos_dentro: int
    cupos_disponibles: int
    total_cupos: int
    cupos_carro_disponibles: int
    cupos_moto_disponibles: int
    ingresos_hoy: int
    salidas_hoy: int
    porcentaje_ocupacion: float
    actividad_reciente: list[ActividadRecienteItem]
    vehiculos_activos: list[VehiculoActivoItem]


@router.get("/resumen", response_model=MetricasPanelRespuesta)
def obtener_resumen_panel(
    sede_id: uuid.UUID | None = Query(None, description="ID de la sede"),
    sesion: Session = Depends(obtener_sesion),
) -> Any:
    # 1. Obtener la sede (si no se envía, tomar la primera registrada)
    if sede_id:
        sede = sesion.get(SedeModelo, sede_id)
    else:
        sede = sesion.scalars(select(SedeModelo).limit(1)).first()

    if not sede:
        # Valores por defecto de contingencia
        total_cupos = 200
        cupos_carro = 128
        cupos_moto = 72
        sede_nombre = "Sede Principal"
        sede_uuid_str = str(uuid.uuid4())
    else:
        cupos_carro = sede.cupos_carro
        cupos_moto = sede.cupos_moto
        total_cupos = cupos_carro + cupos_moto
        sede_nombre = sede.nombre
        sede_uuid_str = str(sede.id)

    # 2. Vehículos actualmente dentro (fecha_hora_salida IS NULL)
    stmt_dentro = select(EstanciaModelo).where(EstanciaModelo.fecha_hora_salida.is_(None))
    if sede:
        stmt_dentro = stmt_dentro.where(EstanciaModelo.sede_id == sede.id)

    estancias_activas = sesion.scalars(
        stmt_dentro.order_by(EstanciaModelo.fecha_hora_entrada.desc())
    ).all()

    vehiculos_dentro = len(estancias_activas)

    # Desglose por tipo
    carros_dentro = sum(
        1 for e in estancias_activas if (e.tipo_vehiculo or "").upper() in ("CARRO", "AUTOMOVIL")
    )
    motos_dentro = sum(1 for e in estancias_activas if (e.tipo_vehiculo or "").upper() == "MOTO")

    cupos_carro_disp = max(0, cupos_carro - carros_dentro)
    cupos_moto_disp = max(0, cupos_moto - motos_dentro)
    cupos_disponibles = max(0, total_cupos - vehiculos_dentro)

    porcentaje_ocupacion = (
        round((vehiculos_dentro / total_cupos * 100), 1) if total_cupos > 0 else 0.0
    )

    # 3. Ingresos y salidas de hoy
    ahora_utc = datetime.now(UTC)
    inicio_hoy = datetime(ahora_utc.year, ahora_utc.month, ahora_utc.day, tzinfo=UTC)

    stmt_ingresos_hoy = select(func.count(EstanciaModelo.id)).where(
        EstanciaModelo.fecha_hora_entrada >= inicio_hoy
    )
    stmt_salidas_hoy = select(func.count(EstanciaModelo.id)).where(
        EstanciaModelo.fecha_hora_salida.is_not(None),
        EstanciaModelo.fecha_hora_salida >= inicio_hoy,
    )
    if sede:
        stmt_ingresos_hoy = stmt_ingresos_hoy.where(EstanciaModelo.sede_id == sede.id)
        stmt_salidas_hoy = stmt_salidas_hoy.where(EstanciaModelo.sede_id == sede.id)

    ingresos_hoy = sesion.scalar(stmt_ingresos_hoy) or 0
    salidas_hoy = sesion.scalar(stmt_salidas_hoy) or 0

    # 4. Actividad reciente (últimos eventos de lectura o estancias)
    stmt_eventos = (
        select(EventoLecturaModelo).order_by(EventoLecturaModelo.fecha_hora.desc()).limit(8)
    )
    if sede:
        stmt_eventos = stmt_eventos.where(EventoLecturaModelo.sede_id == sede.id)
    eventos = sesion.scalars(stmt_eventos).all()

    actividad: list[ActividadRecienteItem] = []
    for ev in eventos:
        hora_str = ev.fecha_hora.strftime("%H:%M") if ev.fecha_hora else "--:--"
        actividad.append(
            ActividadRecienteItem(
                tipo="LECTURA",
                placa=ev.placa or "SIN_PLACA",
                hora=hora_str,
                estado=ev.estado or "REGISTRADO",
            )
        )

    # Si no hay eventos LPR aún, usamos las estancias recientes como actividad
    if not actividad:
        for est in estancias_activas[:5]:
            hora_str = (
                est.fecha_hora_entrada.strftime("%H:%M") if est.fecha_hora_entrada else "--:--"
            )
            actividad.append(
                ActividadRecienteItem(
                    tipo="INGRESO",
                    placa=est.placa,
                    hora=hora_str,
                    estado="Dentro",
                )
            )

    # 5. Lista de vehículos dentro
    lista_activos: list[VehiculoActivoItem] = []
    for est in estancias_activas:
        hora_str = est.fecha_hora_entrada.strftime("%H:%M") if est.fecha_hora_entrada else "--:--"
        tipo_legible = (
            "Automóvil"
            if (est.tipo_vehiculo or "").upper() in ("CARRO", "AUTOMOVIL")
            else "Motocicleta"
        )
        lista_activos.append(
            VehiculoActivoItem(
                placa=est.placa,
                tipo_vehiculo=tipo_legible,
                ingreso=hora_str,
                estado="Dentro",
            )
        )

    return MetricasPanelRespuesta(
        sede_id=sede_uuid_str,
        sede_nombre=sede_nombre,
        vehiculos_dentro=vehiculos_dentro,
        cupos_disponibles=cupos_disponibles,
        total_cupos=total_cupos,
        cupos_carro_disponibles=cupos_carro_disp,
        cupos_moto_disponibles=cupos_moto_disp,
        ingresos_hoy=ingresos_hoy,
        salidas_hoy=salidas_hoy,
        porcentaje_ocupacion=porcentaje_ocupacion,
        actividad_reciente=actividad,
        vehiculos_activos=lista_activos,
    )
