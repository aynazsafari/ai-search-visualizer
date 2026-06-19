"""
algorithms/dfs.py
Depth-First Search.

Strategy: LIFO frontier (stack). Dives as deep as possible before backtracking.
Finds *a* path quickly on many maps but it is not optimal in steps or in cost.
"""

import time

from core.grid_utils import get_neighbors, cell_cost, reconstruct_path, validate_grid
from core.result_schema import make_result, new_step


def run(grid, start, goal, **kwargs):
    start_time = time.time()
    ok, msg = validate_grid(grid, start, goal)
    if not ok:
        return make_result("DFS", False, execution_time=time.time() - start_time, message=msg)

    stack = [start]
    parent = {start: None}
    cost = {start: 0}
    depth = {start: 0}

    explored, visited_order = [], []
    frontier_history, explored_history, steps_log = [], [], []
    expanded_nodes = generated_nodes = step = 0

    while stack:
        current = stack.pop()
        visited_order.append(current)
        if current not in explored:
            explored.append(current)
        if current == goal:
            break

        # New neighbours in U, D, L, R order; pushed reversed so they pop
        # back in that same priority order.
        fresh = [nb for nb in get_neighbors(grid, current) if nb not in parent]
        children = list(fresh)
        for nb in reversed(fresh):
            parent[nb] = current
            cost[nb] = cost[current] + cell_cost(grid[nb[0]][nb[1]])
            depth[nb] = depth[current] + 1
            stack.append(nb)
            generated_nodes += 1

        expanded_nodes += 1
        step += 1
        frontier_history.append(list(stack))
        explored_history.append(list(explored))
        steps_log.append(new_step(step, current, children, list(stack),
                                  explored, cost[current], depth[current]))

    found = goal in parent
    path = reconstruct_path(parent, start, goal) if found else []
    return make_result(
        "DFS", found, path, cost.get(goal) if found else None,
        expanded_nodes, generated_nodes, visited_order,
        frontier_history, explored_history, steps_log,
        time.time() - start_time,
    )
