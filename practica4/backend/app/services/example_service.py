from __future__ import annotations

import json

from app.core.config import EXAMPLES_DIR
from app.models.schemas import MazeExample


class ExampleNotFoundError(LookupError):
    pass


def get_examples() -> list[MazeExample]:
    examples: list[MazeExample] = []
    for path in sorted(EXAMPLES_DIR.glob("maze_*.json")):
        with path.open(encoding="utf-8") as source:
            examples.append(MazeExample.model_validate(json.load(source)))
    return examples


def get_example(example_id: int) -> MazeExample:
    for example in get_examples():
        if example.id == example_id:
            return example
    raise ExampleNotFoundError(f"No existe el laberinto predefinido {example_id}.")
