from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MapConfiguration(StrictModel):
    width: int = Field(ge=10, le=30)
    height: int = Field(ge=10, le=30)


class RobotConfiguration(StrictModel):
    id: str = Field(min_length=1, max_length=40, pattern=r"^[a-zA-Z0-9_-]+$")
    x: int = Field(ge=1)
    y: int = Field(ge=1)
    status: str = "libre"
    carrying: str = "none"


class PackageConfiguration(StrictModel):
    id: str = Field(min_length=1, max_length=40, pattern=r"^[a-zA-Z0-9_-]+$")
    x: int = Field(ge=1)
    y: int = Field(ge=1)
    zone: str = Field(min_length=1, max_length=40)
    status: str = "pendiente"


class ZoneConfiguration(StrictModel):
    id: str = Field(min_length=1, max_length=40, pattern=r"^[a-zA-Z0-9_-]+$")
    x: int = Field(ge=1)
    y: int = Field(ge=1)


class ObstacleConfiguration(StrictModel):
    x: int = Field(ge=1)
    y: int = Field(ge=1)


class ScenarioConfiguration(StrictModel):
    map: MapConfiguration
    robots: list[RobotConfiguration] = Field(min_length=1)
    packages: list[PackageConfiguration] = Field(default_factory=list)
    zones: list[ZoneConfiguration] = Field(min_length=2)
    obstacles: list[ObstacleConfiguration] = Field(min_length=8)

    @model_validator(mode="after")
    def validate_warehouse(self):
        width, height = self.map.width, self.map.height
        groups = (
            ("robot", self.robots),
            ("paquete", self.packages),
            ("zona", self.zones),
            ("obstaculo", self.obstacles),
        )
        occupied: dict[tuple[int, int], str] = {}
        for label, items in groups:
            for item in items:
                if item.x > width or item.y > height:
                    raise ValueError(f"{label} fuera del mapa en ({item.x},{item.y})")
                position = (item.x, item.y)
                if position in occupied:
                    raise ValueError(
                        f"colision en ({item.x},{item.y}) entre {occupied[position]} y {label}"
                    )
                occupied[position] = label

        robot_ids = [item.id for item in self.robots]
        package_ids = [item.id for item in self.packages]
        zone_ids = [item.id for item in self.zones]
        if len(robot_ids) != len(set(robot_ids)):
            raise ValueError("los identificadores de robot deben ser unicos")
        if len(package_ids) != len(set(package_ids)):
            raise ValueError("los identificadores de paquete deben ser unicos")
        if len(zone_ids) != len(set(zone_ids)):
            raise ValueError("los identificadores de zona deben ser unicos")
        valid_zones = set(zone_ids)
        for package in self.packages:
            if package.zone not in valid_zones:
                raise ValueError(f"el paquete {package.id} tiene una zona de entrega invalida")
        return self


class ScenarioCreate(StrictModel):
    name: str = Field(min_length=3, max_length=80)
    configuration: ScenarioConfiguration


class ScenarioUpdate(StrictModel):
    name: str = Field(min_length=3, max_length=80)
    configuration: ScenarioConfiguration


class ScenarioApply(StrictModel):
    configuration: ScenarioConfiguration
