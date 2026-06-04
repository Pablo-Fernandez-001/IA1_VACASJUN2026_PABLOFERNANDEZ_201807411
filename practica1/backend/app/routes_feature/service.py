from app.prolog_engine.engine import PrologEngine
from app.prolog_engine.serializer import normalize_route, normalize_routes


class RoutesService:
    def __init__(self):
        self.engine = PrologEngine()

    def get_shortest_route(self, origen: str, destino: str):
        origen_atom = self.engine.sanitize_atom(origen)
        destino_atom = self.engine.sanitize_atom(destino)

        query = f"ruta_mas_corta({origen_atom}, {destino_atom}, Ruta, Distancia)"
        result = self.engine.query(query)

        if not result:
            return None

        return {
            "ruta": normalize_route(result[0]["Ruta"]),
            "distancia": result[0]["Distancia"]
        }

    def get_all_routes(self, origen: str, destino: str):
        origen_atom = self.engine.sanitize_atom(origen)
        destino_atom = self.engine.sanitize_atom(destino)

        query = f"rutas_posibles({origen_atom}, {destino_atom}, Rutas)"
        result = self.engine.query(query)

        if not result:
            return []

        return normalize_routes(result[0]["Rutas"])