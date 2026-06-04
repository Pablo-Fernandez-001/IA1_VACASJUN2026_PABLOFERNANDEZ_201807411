import re
from app.core.config import settings
from pyswip import Prolog


class PrologEngine:
    def __init__(self):
        self.prolog = Prolog()
        self.prolog.consult(str(settings.PROLOG_FILE))

    def query(self, query_text: str):
        return list(self.prolog.query(query_text))

    def sanitize_atom(self, value: str) -> str:
        """
        Convierte texto normal en un atomo valido para Prolog.
        Ejemplo:
        'Puerto Barrios' -> 'puerto_barrios'
        """
        value = value.lower().strip()
        value = value.replace("á", "a")
        value = value.replace("é", "e")
        value = value.replace("í", "i")
        value = value.replace("ó", "o")
        value = value.replace("ú", "u")
        value = value.replace("ñ", "n")
        value = value.replace(" ", "_")

        value = re.sub(r"[^a-z0-9_]", "", value)

        if not value:
            raise ValueError("El nombre de ciudad no puede estar vacio.")

        return value

    def add_connection(self, origen: str, destino: str, distancia: int):
        origen_atom = self.sanitize_atom(origen)
        destino_atom = self.sanitize_atom(destino)

        query_text = f"agregar_conexion({origen_atom}, {destino_atom}, {distancia})"
        result = self.query(query_text)

        if result:
            self.persist_connection(origen_atom, destino_atom, distancia)
            return {
                "origen": origen_atom,
                "destino": destino_atom,
                "distancia": distancia
            }

        return None

    def delete_connection(self, origen: str, destino: str):
        origen_atom = self.sanitize_atom(origen)
        destino_atom = self.sanitize_atom(destino)

        query_text = f"eliminar_conexion({origen_atom}, {destino_atom})"
        self.query(query_text)

        self.remove_connection_from_file(origen_atom, destino_atom)

        return {
            "origen": origen_atom,
            "destino": destino_atom
        }

    def persist_connection(self, origen: str, destino: str, distancia: int):
        line = f"\nconexion({origen}, {destino}, {distancia})."

        content = settings.PROLOG_FILE.read_text(encoding="utf-8")

        if line.strip() not in content:
            with open(settings.PROLOG_FILE, "a", encoding="utf-8") as file:
                file.write(line)

    def remove_connection_from_file(self, origen: str, destino: str):
        content = settings.PROLOG_FILE.read_text(encoding="utf-8").splitlines()

        direct_line = f"conexion({origen}, {destino},"
        inverse_line = f"conexion({destino}, {origen},"

        new_lines = []

        for line in content:
            cleaned = line.strip()
            if cleaned.startswith(direct_line) or cleaned.startswith(inverse_line):
                continue
            new_lines.append(line)

        settings.PROLOG_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")