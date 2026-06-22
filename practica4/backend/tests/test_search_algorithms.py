import json
from pathlib import Path

import pytest

from app.models.schemas import MazeRequest
from app.services.bfs_service import solve_bfs
from app.services.comparison_service import compare_algorithms
from app.services.dfs_service import solve_dfs
from app.services.maze_validator import MazeValidationError, validate_maze


def as_maze(data: dict) -> MazeRequest:
    return MazeRequest.model_validate(data)


def test_bfs_finds_shortest_path(simple_maze):
    result = solve_bfs(as_maze(simple_maze))
    assert result.path_found is True
    assert result.path_length == 8
    assert result.path[0].model_dump() == simple_maze["start"]
    assert result.path[-1].model_dump() == simple_maze["goal"]
    assert result.nodes_explored == len(result.visited_nodes)


def test_dfs_finds_a_valid_path(simple_maze):
    result = solve_dfs(as_maze(simple_maze))
    obstacle_set = {(item["row"], item["col"]) for item in simple_maze["obstacles"]}
    points = [(item.row, item.col) for item in result.path]
    assert result.path_found is True
    assert all(point not in obstacle_set for point in points)
    assert all(
        abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
        for a, b in zip(points, points[1:])
    )


@pytest.mark.parametrize("solver", [solve_bfs, solve_dfs])
def test_start_equal_to_goal_is_zero_step_solution(solver):
    maze = as_maze(
        {
            "rows": 2,
            "cols": 2,
            "start": {"row": 1, "col": 1},
            "goal": {"row": 1, "col": 1},
            "obstacles": [],
        }
    )
    result = solver(maze)
    assert result.path_found is True
    assert result.path_length == 0
    assert result.nodes_explored == 1


@pytest.mark.parametrize("solver", [solve_bfs, solve_dfs])
def test_unsolvable_maze_returns_safe_result(solver):
    maze = as_maze(
        {
            "rows": 3,
            "cols": 3,
            "start": {"row": 0, "col": 0},
            "goal": {"row": 2, "col": 2},
            "obstacles": [{"row": 1, "col": 2}, {"row": 2, "col": 1}],
        }
    )
    result = solver(maze)
    assert result.path_found is False
    assert result.path == []
    assert result.path_length == 0
    assert result.nodes_explored > 0


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"rows": 0}, "positivos"),
        ({"rows": 101}, "maximo"),
        ({"start": {"row": -1, "col": 0}}, "inicial"),
        ({"goal": {"row": 9, "col": 0}}, "destino"),
        ({"obstacles": [{"row": 7, "col": 0}]}, "obstaculo"),
        (
            {"obstacles": [{"row": 1, "col": 1}, {"row": 1, "col": 1}]},
            "duplicados",
        ),
        ({"obstacles": [{"row": 0, "col": 0}]}, "inicial"),
        ({"obstacles": [{"row": 4, "col": 4}]}, "destino"),
    ],
)
def test_domain_validations(simple_maze, changes, message):
    payload = {**simple_maze, **changes}
    with pytest.raises(MazeValidationError, match=message):
        validate_maze(as_maze(payload))


def test_bfs_is_never_longer_than_dfs_on_all_examples():
    examples_dir = Path(__file__).resolve().parents[2] / "examples"
    for path in examples_dir.glob("maze_*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        maze_data = {key: data[key] for key in ("rows", "cols", "start", "goal", "obstacles")}
        result = compare_algorithms(as_maze(maze_data))
        if result.bfs.path_found and result.dfs.path_found:
            assert result.bfs.path_length <= result.dfs.path_length


def test_comparison_contains_metrics_and_conclusion(simple_maze):
    result = compare_algorithms(as_maze(simple_maze))
    assert result.bfs.algorithm == "BFS"
    assert result.dfs.algorithm == "DFS"
    assert result.differences.nodes_explored == (
        result.bfs.nodes_explored - result.dfs.nodes_explored
    )
    assert "BFS" in result.conclusion
