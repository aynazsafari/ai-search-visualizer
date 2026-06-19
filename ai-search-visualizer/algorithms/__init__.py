"""
algorithms package: every search algorithm exposes a single
    run(grid, start, goal, **kwargs) -> result dict
function, all returning the identical schema from core.result_schema.
"""

from algorithms import bfs, dfs, ucs, dls, ids, greedy, astar

# Ordered registry used by the CLI and the Streamlit frontend.
ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "DLS": dls,
    "IDS": ids,
    "Greedy": greedy,
    "A*": astar,
}

UNINFORMED = ["BFS", "DFS", "UCS", "DLS", "IDS"]
INFORMED = ["Greedy", "A*"]

__all__ = ["ALGORITHMS", "UNINFORMED", "INFORMED",
           "bfs", "dfs", "ucs", "dls", "ids", "greedy", "astar"]
