from __future__ import annotations

from collections import deque
from time import perf_counter

from app.models.schemas import MazeRequest, SearchResult
from app.services.maze_validator import valid_neighbors, validate_maze
from app.services.search_utils import as_coordinates, reconstruct_path


def solve_bfs(maze: MazeRequest) -> SearchResult:
    """Resuelve el laberinto con BFS manual y una cola FIFO."""

    validate_maze(maze)
    started_at = perf_counter()
    start = (maze.start.row, maze.start.col)
    goal = (maze.goal.row, maze.goal.col)
    obstacles = {(point.row, point.col) for point in maze.obstacles}

    frontier: deque[tuple[int, int]] = deque([start])
    discovered = {start}
    parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    visited_order: list[tuple[int, int]] = []
    found = False

    while frontier:
        current = frontier.popleft()
        visited_order.append(current)
        if current == goal:
            found = True
            break

        for neighbor in valid_neighbors(current, maze.rows, maze.cols, obstacles):
            if neighbor not in discovered:
                discovered.add(neighbor)
                parents[neighbor] = current
                frontier.append(neighbor)

    elapsed_ms = round((perf_counter() - started_at) * 1000, 6)
    path = reconstruct_path(parents, goal) if found else []
    return SearchResult(
        algorithm="BFS",
        path_found=found,
        path=path,
        visited_nodes=as_coordinates(visited_order),
        nodes_explored=len(visited_order),
        path_length=max(0, len(path) - 1),
        execution_time_ms=elapsed_ms,
        message=(
            "Ruta encontrada correctamente."
            if found
            else "No existe una ruta valida entre el origen y el destino."
        ),
    )
