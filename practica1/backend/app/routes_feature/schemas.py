from pydantic import BaseModel


class RouteResponse(BaseModel):
    ruta: list[str]
    distancia: int