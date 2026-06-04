from fastapi import APIRouter, HTTPException
from app.routes_feature.service import RoutesService


router = APIRouter(
    prefix="/rutas",
    tags=["Rutas"]
)

service = RoutesService()


@router.get("/mas-corta")
def get_shortest_route(origen: str, destino: str):
    result = service.get_shortest_route(origen, destino)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No existe una ruta disponible entre las ciudades indicadas."
        )

    return result


@router.get("/todas")
def get_all_routes(origen: str, destino: str):
    result = service.get_all_routes(origen, destino)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron rutas entre las ciudades indicadas."
        )

    return {
        "rutas": result
    }