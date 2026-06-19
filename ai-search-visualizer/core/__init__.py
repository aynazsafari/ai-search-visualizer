"""
core package: shared utilities for the AI Search Visualizer.

Note: `visualizer` is intentionally NOT imported here, because it depends on
Streamlit. Importing it eagerly would force the command-line runner (main.py)
to require Streamlit too. Import it explicitly from app.py instead.
"""

from core.grid_utils import (
    load_map,
    get_neighbors,
    cell_cost,
    manhattan_distance,
    reconstruct_path,
    validate_grid,
)
from core.result_schema import make_result, new_step, ALGORITHM_TYPE

__all__ = [
    "load_map",
    "get_neighbors",
    "cell_cost",
    "manhattan_distance",
    "reconstruct_path",
    "validate_grid",
    "make_result",
    "new_step",
    "ALGORITHM_TYPE",
]
