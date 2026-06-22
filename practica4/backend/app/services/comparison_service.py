from __future__ import annotations

from app.models.schemas import ComparisonDifferences, ComparisonResult, MazeRequest
from app.services.bfs_service import solve_bfs
from app.services.dfs_service import solve_dfs


def _conclusion(bfs, dfs) -> str:
    if not bfs.path_found and not dfs.path_found:
        return "Ningun algoritmo encontro una ruta valida para este laberinto."
    if bfs.path_found and not dfs.path_found:
        return "BFS encontro una ruta y DFS no encontro solucion."
    if dfs.path_found and not bfs.path_found:
        return "DFS encontro una ruta y BFS no encontro solucion."

    if bfs.path_length < dfs.path_length:
        route_note = "BFS encontro una ruta mas corta."
    elif dfs.path_length < bfs.path_length:
        route_note = "DFS encontro una ruta mas corta en este orden de exploracion."
    else:
        route_note = "Ambos encontraron rutas con la misma longitud."

    if bfs.nodes_explored < dfs.nodes_explored:
        effort_note = "BFS exploro menos nodos."
    elif dfs.nodes_explored < bfs.nodes_explored:
        effort_note = "DFS exploro menos nodos."
    else:
        effort_note = "Ambos exploraron la misma cantidad de nodos."

    return f"{route_note} {effort_note} BFS garantiza la ruta minima en esta cuadricula sin pesos."


def compare_algorithms(maze: MazeRequest) -> ComparisonResult:
    bfs = solve_bfs(maze)
    dfs = solve_dfs(maze)
    return ComparisonResult(
        bfs=bfs,
        dfs=dfs,
        differences=ComparisonDifferences(
            path_length=bfs.path_length - dfs.path_length,
            nodes_explored=bfs.nodes_explored - dfs.nodes_explored,
            execution_time_ms=round(bfs.execution_time_ms - dfs.execution_time_ms, 6),
        ),
        conclusion=_conclusion(bfs, dfs),
    )
