from app.prolog_engine.engine import PrologEngine


class ConnectionsService:
    def __init__(self):
        self.engine = PrologEngine()

    def create_connection(self, origen: str, destino: str, distancia: int):
        return self.engine.add_connection(origen, destino, distancia)

    def delete_connection(self, origen: str, destino: str):
        return self.engine.delete_connection(origen, destino)