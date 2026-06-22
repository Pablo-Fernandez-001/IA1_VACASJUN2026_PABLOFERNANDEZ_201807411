from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Coordinate(BaseModel):
    """Posicion inmutable dentro de una cuadricula."""

    model_config = ConfigDict(frozen=True)

    row: int = Field(..., description="Fila basada en cero")
    col: int = Field(..., description="Columna basada en cero")


class MazeRequest(BaseModel):
    """Configuracion completa de un laberinto enviada por el cliente."""

    model_config = ConfigDict(extra="forbid")

    rows: int = Field(..., description="Numero de filas")
    cols: int = Field(..., description="Numero de columnas")
    start: Coordinate
    goal: Coordinate
    obstacles: list[Coordinate] = Field(default_factory=list)


class SearchResult(BaseModel):
    algorithm: Literal["BFS", "DFS"]
    path_found: bool
    path: list[Coordinate]
    visited_nodes: list[Coordinate]
    nodes_explored: int
    path_length: int
    execution_time_ms: float
    message: str


class ComparisonDifferences(BaseModel):
    """Diferencias calculadas como BFS menos DFS."""

    path_length: int
    nodes_explored: int
    execution_time_ms: float


class ComparisonResult(BaseModel):
    bfs: SearchResult
    dfs: SearchResult
    differences: ComparisonDifferences
    conclusion: str


class MazeExample(MazeRequest):
    id: int
    name: str
    description: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
