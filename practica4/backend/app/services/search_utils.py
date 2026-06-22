from __future__ import annotations

from app.models.schemas import Coordinate


def reconstruct_path(
    parents: dict[tuple[int, int], tuple[int, int] | None],
    goal: tuple[int, int],
) -> list[Coordinate]:
    path: list[tuple[int, int]] = []
    current: tuple[int, int] | None = goal
    while current is not None:
        path.append(current)
        current = parents[current]
    path.reverse()
    return [Coordinate(row=row, col=col) for row, col in path]


def as_coordinates(points: list[tuple[int, int]]) -> list[Coordinate]:
    return [Coordinate(row=row, col=col) for row, col in points]
