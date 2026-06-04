from fastapi import APIRouter
from app.cities_feature.service import CitiesService


router = APIRouter(
    prefix="/ciudades",
    tags=["Ciudades"]
)

service = CitiesService()


@router.get("/")
def get_cities():
    return {
        "ciudades": service.get_cities()
    }