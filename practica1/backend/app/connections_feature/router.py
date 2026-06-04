from fastapi import APIRouter, HTTPException
from app.connections_feature.schemas import ConnectionCreate, ConnectionDelete
from app.connections_feature.service import ConnectionsService


router = APIRouter(
    prefix="/conexiones",
    tags=["Conexiones"]
)

service = ConnectionsService()


@router.post("/")
def create_connection(data: ConnectionCreate):
    created = service.create_connection(
        data.origen,
        data.destino,
        data.distancia
    )

    if created is None:
        raise HTTPException(
            status_code=400,
            detail="No se pudo agregar la conexión. Puede que ya exista o que los datos sean inválidos."
        )

    return {
        "mensaje": "Conexión agregada dinámicamente.",
        "conexion": created
    }


@router.delete("/")
def delete_connection(data: ConnectionDelete):
    deleted = service.delete_connection(
        data.origen,
        data.destino
    )

    return {
        "mensaje": "Conexión eliminada dinámicamente.",
        "conexion": deleted
    }