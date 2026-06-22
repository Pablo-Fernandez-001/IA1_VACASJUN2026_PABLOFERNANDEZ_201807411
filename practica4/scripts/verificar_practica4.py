"""Auditoria local de entregables de RoboMaze, sin modificar archivos."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"


def contains(path: str, *tokens: str) -> bool:
    content = (ROOT / path).read_text(encoding="utf-8").lower()
    return all(token.lower() in content for token in tokens)


def valid_examples() -> bool:
    paths = sorted((ROOT / "examples").glob("maze_*.json"))
    if len(paths) != 5:
        return False
    for expected_id, path in enumerate(paths, 1):
        data = json.loads(path.read_text(encoding="utf-8"))
        required = {"id", "name", "description", "rows", "cols", "start", "goal", "obstacles"}
        if set(data) != required or data["id"] != expected_id:
            return False
        if data["rows"] <= 0 or data["cols"] <= 0:
            return False
        keys = [(point["row"], point["col"]) for point in data["obstacles"]]
        if len(keys) != len(set(keys)):
            return False
    return True


def tests_pass() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        check=False,
    )
    last_line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else result.stderr.strip()
    print(f"    pytest: {last_line}")
    return result.returncode == 0


def main() -> int:
    required_backend = [
        "backend/app/main.py",
        "backend/app/api/maze_routes.py",
        "backend/app/models/schemas.py",
        "backend/app/services/bfs_service.py",
        "backend/app/services/dfs_service.py",
        "backend/app/services/maze_validator.py",
        "backend/app/services/comparison_service.py",
    ]
    required_docs = [
        "README.md",
        "MANUAL_TECNICO.md",
        "MANUAL_USUARIO.md",
        "ENTREGA_UEDI.md",
        "transcripcion_practica4.md",
    ]
    evidence = [ROOT / "docs" / "evidencias" / f"0{index}_{name}.png" for index, name in [
        (1, "inicio"),
        (2, "laberinto_predefinido"),
        (3, "bfs_resultado"),
        (4, "dfs_resultado"),
        (5, "comparacion"),
        (6, "sin_ruta"),
    ]]

    checks = [
        ("Backend por capas", all((ROOT / path).is_file() for path in required_backend)),
        ("BFS manual con cola", contains("backend/app/services/bfs_service.py", "deque", "parents", "while frontier")),
        ("DFS manual con pila", contains("backend/app/services/dfs_service.py", "stack", "parents", "while stack")),
        ("Validaciones de dominio", contains("backend/app/services/maze_validator.py", "duplicados", "maximo", "bloqueado")),
        ("Endpoints REST", contains("backend/app/api/maze_routes.py", "/solve/bfs", "/solve/dfs", "/solve/compare", "/examples")),
        ("Cinco ejemplos validos", valid_examples()),
        ("Frontend separado", all((ROOT / path).is_file() for path in ["frontend/index.html", "frontend/css/styles.css", "frontend/js/app.js", "frontend/js/api.js", "frontend/js/maze.js"])),
        ("Editor de laberinto", contains("frontend/js/maze.js", "obstacles", "start", "goal", "visited")),
        ("Comparacion visual", contains("frontend/index.html", "comparisonBody", "metricNodes", "metricTime")),
        ("Error de backend", contains("frontend/js/api.js", "No fue posible conectar")),
        ("Documentos obligatorios", all((ROOT / path).is_file() for path in required_docs)),
        ("Arquitectura Mermaid", contains("MANUAL_TECNICO.md", "```mermaid", "arquitectura por capas")),
        ("RF y RNF", contains("MANUAL_TECNICO.md", "requerimientos funcionales", "requerimientos no funcionales")),
        ("Manual con evidencias", contains("MANUAL_USUARIO.md", "01_inicio.png", "06_sin_ruta.png")),
        ("Docker Compose", (ROOT / "docker-compose.yml").is_file()),
        ("Coleccion Postman", (ROOT / "postman/RoboMaze.postman_collection.json").is_file()),
        ("Suite automatizada", tests_pass()),
        ("Evidencias PNG", all(path.is_file() and path.stat().st_size > 1000 for path in evidence)),
        ("Defensa y guia de evidencias", all((ROOT / path).is_file() for path in ["docs/GUIA_DEFENSA.md", "docs/evidencias/README.md"])),
        ("Datos de entrega", contains("ENTREGA_UEDI.md", "201807411", "24/06/2026", "github.com")),
    ]

    passed = 0
    print("\nVERIFICACION ROBOMAZE\n" + "=" * 48)
    for label, ok in checks:
        print(f"[{'OK' if ok else 'FALTA'}] {label}")
        passed += int(ok)
    score = passed * 5
    print("=" * 48)
    print(f"Cobertura local: {score}/100 ({passed}/{len(checks)} controles)")
    if score == 100:
        print("Todo el contenido local verificable esta completo.")
    else:
        print("Revise los controles marcados como FALTA antes de entregar.")
    print("Nota: commits, push y entrega UEDI deben comprobarse externamente.")
    return 0 if score == 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())
