from fastapi import APIRouter

router_estado = APIRouter(tags=["estado"])


@router_estado.get("/estado")
def consultar_estado() -> dict[str, str]:
    return {"estado": "funcionando"}
