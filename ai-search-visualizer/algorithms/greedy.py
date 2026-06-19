"""
algorithms/greedy.py
Greedy Best-First Search.

Evaluation function: f(n) = h(n) = Manhattan distance to the goal.
Always heads toward whatever looks closest. Usually fast, but it ignores the
cost already paid, so the path it returns is not guaranteed to be the cheapest.
"""

import time
import heapq

from core.grid_utils import (
    get_neighbors, cell_cost, manhattan_distance, reconstruct_path, validate_grid,
)
from core.result_schema import make_result, new_step


def run(grid, start, goal, **kwargs):
    start_time = time.time()
    ok, msg = validate_grid(grid, start, goal)
    if not ok:
        return make_result("Greedy", False, execution_time=time.time() - start_time, message=msg)

    # Priority queue entries: (h_value, insertion_counter, node)
    counter = 0
    frontier = [(manhattan_distance(start, goal), counter, start)]
    parent = {start: None}
    cost = {start: 0}
    depth = {start: 0}

    explored, visited_order = [], []
    frontier_history, explored_history, steps_log = [], [], []
    expanded_nodes = generated_nodes = step = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in explored:
            continue
        explored.append(current)
        visited_order.append(current)
        if current == goal:
            break

        children = []
        for nb in get_neighbors(grid, current):
            if nb not in parent:
                parent[nb] = current
                cost[nb] = cost[current] + cell_cost(grid[nb[0]][nb[1]])
                depth[nb] = depth[current] + 1
                counter += 1
                heapq.heappush(frontier, (manhattan_distance(nb, goal), counter, nb))
                children.append(nb)
                generated_nodes += 1

        expanded_nodes += 1
        step += 1
        frontier_nodes = [n for _, _, n in frontier]
        frontier_history.append(frontier_nodes)
        explored_history.append(list(explored))
        steps_log.append(new_step(step, current, children, frontier_nodes,
                                  explored, cost[current], depth[current],
                                  note=f"h={manhattan_distance(current, goal)}"))

    found = goal in parent
    path = reconstruct_path(parent, start, goal) if found else []
    return make_result(
        "Greedy", found, path, cost.get(goal) if found else None,
        expanded_nodes, generated_nodes, visited_order,
        frontier_history, explored_history, steps_log,
        time.time() - start_time,
    )
