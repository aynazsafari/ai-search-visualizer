"""
algorithms/ids.py
Iterative Deepening Search.

Runs Depth-Limited Search repeatedly with the limit growing 0, 1, 2, ... until
the goal is found (or a maximum depth is reached). It combines DFS's small
memory footprint with BFS's guarantee of finding the shallowest goal.

The reported `expanded_nodes` / `generated_nodes` are the *totals* across every
iteration (that is the true work IDS does, including the re-exploration), and
the step log is the concatenation of all iterations, each tagged with its depth
limit so the re-exploration is visible in the visualizer.
"""

import time

from core.grid_utils import validate_grid
from core.result_schema import make_result


def run(grid, start, goal, **kwargs):
    start_time = time.time()
    ok, msg = validate_grid(grid, start, goal)
    if not ok:
        return make_result("IDS", False, execution_time=time.time() - start_time, message=msg)

    # Imported lazily to avoid any import-order issues inside the package.
    from algorithms import dls

    rows, cols = len(grid), len(grid[0])
    # A simple path can be at most rows*cols long, so that is a safe ceiling.
    max_depth = kwargs.get("max_depth", kwargs.get("depth_limit", rows * cols))

    total_expanded = total_generated = 0
    visited_order, steps_log = [], []
    frontier_history, explored_history = [], []
    step_counter = 0
    found = False
    path, total_cost = [], None
    reached_depth = 0

    for d in range(0, max_depth + 1):
        reached_depth = d
        sub = dls.run(grid, start, goal, depth_limit=d)

        total_expanded += sub["expanded_nodes"]
        total_generated += sub["generated_nodes"]
        visited_order.extend(sub["visited_order"])
        frontier_history.extend(sub["frontier_history"])
        explored_history.extend(sub["explored_history"])

        for s in sub["steps_log"]:
            step_counter += 1
            tagged = dict(s)
            tagged["step"] = step_counter
            base = s.get("note", "") or ""
            tagged["note"] = (f"[depth limit = {d}] " + base).strip()
            steps_log.append(tagged)

        if sub["found"]:
            found = True
            path = sub["path"]
            total_cost = sub["cost"]
            break

    if found:
        message = f"Goal found successfully at depth {reached_depth}."
    else:
        message = f"No path found up to maximum depth {max_depth}."

    return make_result(
        "IDS", found, path, total_cost,
        total_expanded, total_generated, visited_order,
        frontier_history, explored_history, steps_log,
        time.time() - start_time, message=message,
    )
