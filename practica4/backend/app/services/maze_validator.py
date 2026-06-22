from __future__ import annotations

from app.core.config import MAX_MAZE_SIZE
from app.models.schemas import Coordinate, MazeRequest


class MazeValidationError(ValueError):
    """Error de dominio con un mensaje apto para mostrar al usuario."""


def _inside(point: Coordinate, rows: int, cols: int) -> bool:
    return 0 <= point.row < rows and 0 <= point.col < cols


def validate_maze(maze: MazeRequest) -> None:
    """Valida reglas que dependen de mas de un campo del laberinto."""

    if maze.rows <= 0 or maze.cols <= 0:
        raise MazeValidationError("Las filas y columnas deben ser numeros positivos.")
    if maze.rows > MAX_MAZE_SIZE or maze.cols > MAX_MAZE_SIZE:
        raise MazeValidationError(
            f"El tamano maximo permitido es {MAX_MAZE_SIZE} x {MAX_MAZE_SIZE}."
        )
    if not _inside(maze.start, maze.rows, maze.cols):
        raise MazeValidationError("El punto inicial esta fuera del laberinto.")
    if not _inside(maze.goal, maze.rows, maze.cols):
        raise MazeValidationError("El punto destino esta fuera del laberinto.")

    obstacle_keys = [(point.row, point.col) for point in maze.obstacles]
    for point in maze.obstacles:
        if not _inside(point, maze.rows, maze.cols):
            raise MazeValidationError(
                f"El obstaculo ({point.row}, {point.col}) esta fuera del laberinto."
            )
    if len(obstacle_keys) != len(set(obstacle_keys)):
        raise MazeValidationError("No se permiten obstaculos duplicados.")

    obstacle_set = set(obstacle_keys)
    if (maze.start.row, maze.start.col) in obstacle_set:
        raise MazeValidationError("El punto inicial no puede estar bloqueado.")
    if (maze.goal.row, maze.goal.col) in obstacle_set:
        raise MazeValidationError("El punto destino no puede estar bloqueado.")


def valid_neighbors(
    current: tuple[int, int],
    rows: int,
    cols: int,
    obstacles: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Retorna vecinos transitables en orden arriba, derecha, abajo, izquierda."""

    row, col = current
    candidates = [
        (row - 1, col),
        (row, col + 1),
        (row + 1, col),
        (row, col - 1),
    ]
    return [
        point
        for point in candidates
        if 0 <= point[0] < rows and 0 <= point[1] < cols and point not in obstacles
    ]
