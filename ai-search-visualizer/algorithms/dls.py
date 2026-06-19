"""
algorithms/dls.py
Depth-Limited Search.

DFS that refuses to expand any node deeper than `depth_limit`. When it hits a
node at the limit that still has unexplored children, that is a *cutoff* and it
is recorded in the step log. Cycle checking is done along the current branch
only (the path from start to the node), which keeps the search correct and
complete up to the depth limit.

Accepts both `depth_limit` and the legacy `limit` keyword:
    limit = kwargs.get("depth_limit", kwargs.get("limit", 10))
"""

import time

from core.grid_utils import get_neighbors, cell_cost, validate_grid
from core.result_schema import make_result, new_step


def run(grid, start, goal, **kwargs):
    start_time = time.time()
    depth_limit = kwargs.get("depth_limit", kwargs.get("limit", 10))

    ok, msg = validate_grid(grid, start, goal)
    if not ok:
        return make_result("DLS", False, execution_time=time.time() - start_time, message=msg)

    # Stack entries: (node, depth, path_tuple, path_cost)
    stack = [(start, 0, (start,), 0)]

    explored, visited_order = [], []
    frontier_history, explored_history, steps_log = [], [], []
    expanded_nodes = generated_nodes = step = 0
    cutoff_occurred = False
    found = False
    goal_path, goal_cost = [], None

    while stack:
        current, depth, path, pcost = stack.pop()
        visited_order.append(current)
        if current not in explored:
            explored.append(current)
        step += 1
        frontier_nodes = [n for n, _, _, _ in stack]

        if current == goal:
            found = True
            goal_path, goal_cost = list(path), pcost
            frontier_history.append(frontier_nodes)
            explored_history.append(list(explored))
            steps_log.append(new_step(step, current, [], frontier_nodes, explored,
                                      pcost, depth, cutoff=False, note="Goal reached."))
            break

        if depth >= depth_limit:
            # Cannot go deeper: this is a cutoff.
            cutoff_occurred = True
            frontier_history.append(frontier_nodes)
            explored_history.append(list(explored))
            steps_log.append(new_step(step, current, [], frontier_nodes, explored,
                                      pcost, depth, cutoff=True,
                                      note=f"Depth limit {depth_limit} reached - cutoff."))
            continue

        # Expand. Avoid revisiting nodes already on this branch (cycle check).
        fresh = [nb for nb in get_neighbors(grid, current) if nb not in path]
        children = list(fresh)
        for nb in reversed(fresh):
            ncost = pcost + cell_cost(grid[nb[0]][nb[1]])
            stack.append((nb, depth + 1, path + (nb,), ncost))
            generated_nodes += 1

        expanded_nodes += 1
        frontier_history.append([n for n, _, _, _ in stack])
        explored_history.append(list(explored))
        steps_log.append(new_step(step, current, children,
                                  [n for n, _, _, _ in stack], explored,
                                  pcost, depth, cutoff=False))

    if found:
        message = f"Goal found successfully within depth limit {depth_limit}."
    elif cutoff_occurred:
        message = f"No path found within depth limit {depth_limit} (cutoff occurred)."
    else:
        message = "No path found (search space exhausted before reaching the limit)."

    return make_result(
        "DLS", found, goal_path, goal_cost,
        expanded_nodes, generated_nodes, visited_order,
        frontier_history, explored_history, steps_log,
        time.time() - start_time, message=message,
    )
