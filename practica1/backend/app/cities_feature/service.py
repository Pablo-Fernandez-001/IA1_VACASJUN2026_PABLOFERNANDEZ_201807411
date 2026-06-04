from app.prolog_engine.engine import PrologEngine


class CitiesService:
    def __init__(self):
        self.engine = PrologEngine()

    def get_cities(self):
        result = self.engine.query("ciudades(Ciudades)")

        if not result:
            return []

        return [str(city) for city in result[0]["Ciudades"]]