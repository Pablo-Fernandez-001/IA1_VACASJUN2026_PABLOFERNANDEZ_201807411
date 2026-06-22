from fastapi import APIRouter, HTTPException

from app.models.schemas import ComparisonResult, MazeExample, MazeRequest, SearchResult
from app.services.bfs_service import solve_bfs
from app.services.comparison_service import compare_algorithms
from app.services.dfs_service import solve_dfs
from app.services.example_service import ExampleNotFoundError, get_example, get_examples
from app.services.maze_validator import MazeValidationError


router = APIRouter(prefix="/api/maze", tags=["Laberintos"])


def _domain_error(error: MazeValidationError) -> HTTPException:
    return HTTPException(status_code=422, detail=str(error))


@router.post("/solve/bfs", response_model=SearchResult)
def bfs_endpoint(maze: MazeRequest) -> SearchResult:
    try:
        return solve_bfs(maze)
    except MazeValidationError as error:
        raise _domain_error(error) from error


@router.post("/solve/dfs", response_model=SearchResult)
def dfs_endpoint(maze: MazeRequest) -> SearchResult:
    try:
        return solve_dfs(maze)
    except MazeValidationError as error:
        raise _domain_error(error) from error


@router.post("/solve/compare", response_model=ComparisonResult)
def compare_endpoint(maze: MazeRequest) -> ComparisonResult:
    try:
        return compare_algorithms(maze)
    except MazeValidationError as error:
        raise _domain_error(error) from error


@router.get("/examples", response_model=list[MazeExample])
def examples_endpoint() -> list[MazeExample]:
    return get_examples()


@router.get("/examples/{example_id}", response_model=MazeExample)
def example_endpoint(example_id: int) -> MazeExample:
    try:
        return get_example(example_id)
    except ExampleNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
