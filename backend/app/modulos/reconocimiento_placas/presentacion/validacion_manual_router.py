from fastapi import APIRouter, HTTPException, status

from app.modulos.reconocimiento_placas.aplicacion.casos_uso_lpr import (
    ValidarLecturaBajaConfianza,
)
from app.modulos.reconocimiento_placas.presentacion.esquemas_lpr import (
    LecturaLPREsquema,
    ValidarLecturaManualSolicitud,
)

router = APIRouter(
    prefix="/lpr",
    tags=["Reconocimiento de Placas (LPR)"],
)


@router.post(
    "/validar-manual",
    response_model=LecturaLPREsquema,
    status_code=status.HTTP_200_OK,
    summary="Validar y corregir lectura manual de baja confianza (S201)",
)
def validar_lectura_manual(
    datos: ValidarLecturaManualSolicitud,
) -> LecturaLPREsquema:
    caso_uso = ValidarLecturaBajaConfianza()

    try:
        resultado = caso_uso.ejecutar(
            carril_id=datos.carril_id,
            placa_confirmada=datos.placa_confirmada,
            operador_id=datos.operador_id,
            placa_detectada_previa=datos.placa_detectada_previa,
            confianza_previa=datos.confianza_previa,
            umbral_confianza=datos.umbral_confianza,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err

    return LecturaLPREsquema(
        id=resultado.id,
        carril_id=resultado.carril_id,
        placa=resultado.placa,
        confianza=resultado.confianza,
        origen=resultado.origen,
        estado=resultado.estado,
        tipo_vehiculo=resultado.tipo_vehiculo,
        placa_original_detectada=resultado.placa_original_detectada,
        operador_id=resultado.operador_id,
        requiere_confirmacion_manual=resultado.requiere_confirmacion_manual,
    )
