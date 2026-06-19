"""
algorithms/bfs.py
Breadth-First Search.

Strategy: FIFO frontier. Expands the shallowest unexpanded node first, so it
finds the path with the fewest *steps*. It is cost-optimal only when every
step costs the same.
"""

import time
from collections import deque

from core.grid_utils import get_neighbors, cell_cost, reconstruct_path, validate_grid
from core.result_schema import make_result, new_step


def run(grid, start, goal, **kwargs):
    start_time = time.time()
    ok, msg = validate_grid(grid, start, goal)
    if not ok:
        return make_result("BFS", False, execution_time=time.time() - start_time, message=msg)

    frontier = deque([start])
    parent = {start: None}
    cost = {start: 0}
    depth = {start: 0}

    explored, visited_order = [], []
    frontier_history, explored_history, steps_log = [], [], []
    expanded_nodes = generated_nodes = step = 0

    while frontier:
        current = frontier.popleft()
        visited_order.append(current)
        if current not in explored:
            explored.append(current)
        if current == goal:
            break

        children = []
        for nb in get_neighbors(grid, current):
            if nb not in parent:
                parent[nb] = current
                cost[nb] = cost[current] + cell_cost(grid[nb[0]][nb[1]])
                depth[nb] = depth[current] + 1
                frontier.append(nb)
                children.append(nb)
                generated_nodes += 1

        expanded_nodes += 1
        step += 1
        frontier_history.append(list(frontier))
        explored_history.append(list(explored))
        steps_log.append(new_step(step, current, children, list(frontier),
                                  explored, cost[current], depth[current]))

    found = goal in parent
    path = reconstruct_path(parent, start, goal) if found else []
    return make_result(
        "BFS", found, path, cost.get(goal) if found else None,
        expanded_nodes, generated_nodes, visited_order,
        frontier_history, explored_history, steps_log,
        time.time() - start_time,
    )
