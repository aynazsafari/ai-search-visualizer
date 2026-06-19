"""
algorithms/astar.py
A* Search.

Evaluation function: f(n) = g(n) + h(n), where g is the real cost so far and h
is the Manhattan distance. With an admissible heuristic (Manhattan is admissible
on a 4-connected grid) A* returns an optimal-cost path while usually expanding
far fewer nodes than UCS.
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
        return make_result("A*", False, execution_time=time.time() - start_time, message=msg)

    # Priority queue entries: (f_cost, insertion_counter, node)
    counter = 0
    frontier = [(manhattan_distance(start, goal), counter, start)]
    parent = {start: None}
    cost = {start: 0}        # g(n): real cost from start
    depth = {start: 0}

    explored, visited_order = [], []
    frontier_history, explored_history, steps_log = [], [], []
    expanded_nodes = generated_nodes = step = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in explored:
            continue  # an equal-or-cheaper copy was already expanded
        explored.append(current)
        visited_order.append(current)
        if current == goal:
            break

        children = []
        for nb in get_neighbors(grid, current):
            new_cost = cost[current] + cell_cost(grid[nb[0]][nb[1]])
            if nb not in cost or new_cost < cost[nb]:
                cost[nb] = new_cost
                parent[nb] = current
                depth[nb] = depth[current] + 1
                f_cost = new_cost + manhattan_distance(nb, goal)
                counter += 1
                heapq.heappush(frontier, (f_cost, counter, nb))
                children.append(nb)
                generated_nodes += 1

        expanded_nodes += 1
        step += 1
        frontier_nodes = [n for _, _, n in frontier]
        frontier_history.append(frontier_nodes)
        explored_history.append(list(explored))
        f_here = cost[current] + manhattan_distance(current, goal)
        steps_log.append(new_step(step, current, children, frontier_nodes,
                                  explored, cost[current], depth[current],
                                  note=f"g={cost[current]}, f={f_here}"))

    found = goal in parent
    path = reconstruct_path(parent, start, goal) if found else []
    return make_result(
        "A*", found, path, cost.get(goal) if found else None,
        expanded_nodes, generated_nodes, visited_order,
        frontier_history, explored_history, steps_log,
        time.time() - start_time,
    )
