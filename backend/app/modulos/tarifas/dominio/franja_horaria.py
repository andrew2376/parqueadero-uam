from datetime import datetime, time, timedelta
from enum import Enum
from zoneinfo import ZoneInfo


class FranjaHoraria(str, Enum):
    DIURNA = "DIURNA"
    NOCTURNA = "NOCTURNA"


HORA_INICIO_DIURNA = time(6, 0)
HORA_INICIO_NOCTURNA = time(18, 0)


def _convertir_a_zona_local(
    fecha_hora: datetime,
    zona_horaria: str,
) -> datetime:
    if fecha_hora.tzinfo is None or fecha_hora.utcoffset() is None:
        raise ValueError("La fecha y hora debe incluir información de zona horaria.")

    return fecha_hora.astimezone(ZoneInfo(zona_horaria))


def determinar_franja_horaria(
    fecha_hora: datetime,
    zona_horaria: str,
) -> FranjaHoraria:
    fecha_local = _convertir_a_zona_local(fecha_hora, zona_horaria)

    hora = fecha_local.time().replace(tzinfo=None)

    if HORA_INICIO_DIURNA <= hora < HORA_INICIO_NOCTURNA:
        return FranjaHoraria.DIURNA

    return FranjaHoraria.NOCTURNA


def calcular_dia_operativo(
    fecha_hora: datetime,
    zona_horaria: str,
    inicio_dia_operativo: time,
):
    fecha_local = _convertir_a_zona_local(fecha_hora, zona_horaria)

    inicio_hoy = datetime.combine(
        fecha_local.date(),
        inicio_dia_operativo,
        tzinfo=fecha_local.tzinfo,
    )

    if fecha_local < inicio_hoy:
        return fecha_local.date() - timedelta(days=1)

    return fecha_local.date()