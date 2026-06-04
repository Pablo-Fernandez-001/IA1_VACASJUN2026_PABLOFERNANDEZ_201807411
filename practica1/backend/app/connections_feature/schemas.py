from pydantic import BaseModel, Field


class ConnectionCreate(BaseModel):
    origen: str = Field(..., min_length=2)
    destino: str = Field(..., min_length=2)
    distancia: int = Field(..., gt=0)


class ConnectionDelete(BaseModel):
    origen: str = Field(..., min_length=2)
    destino: str = Field(..., min_length=2)