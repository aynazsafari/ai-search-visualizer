"""
algorithms/ucs.py
Uniform-Cost Search (Dijkstra).

Evaluation function: f(n) = g(n), the real accumulated path cost.
Expands the cheapest node first, so it is optimal for any non-negative costs.
This is A* with the heuristic switched off.
"""

import time
import heapq

from core.grid_utils import get_neighbors, cell_cost, reconstruct_path, validate_grid
from core.result_schema import make_result, new_step


def run(grid, start, goal, **kwargs):
    start_time = time.time()
    ok, msg = validate_grid(grid, start, goal)
    if not ok:
        return make_result("UCS", False, execution_time=time.time() - start_time, message=msg)

    # Priority queue entries: (g_cost, insertion_counter, node)
    counter = 0
    frontier = [(0, counter, start)]
    parent = {start: None}
    cost = {start: 0}
    depth = {start: 0}

    explored, visited_order = [], []
    frontier_history, explored_history, steps_log = [], [], []
    expanded_nodes = generated_nodes = step = 0

    while frontier:
        g, _, current = heapq.heappop(frontier)
        if current in explored:
            continue  # a cheaper copy was already expanded (lazy deletion)
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
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, nb))
                children.append(nb)
                generated_nodes += 1

        expanded_nodes += 1
        step += 1
        frontier_nodes = [n for _, _, n in frontier]
        frontier_history.append(frontier_nodes)
        explored_history.append(list(explored))
        steps_log.append(new_step(step, current, children, frontier_nodes,
                                  explored, cost[current], depth[current],
                                  note=f"g={cost[current]}"))

    found = goal in parent
    path = reconstruct_path(parent, start, goal) if found else []
    return make_result(
        "UCS", found, path, cost.get(goal) if found else None,
        expanded_nodes, generated_nodes, visited_order,
        frontier_history, explored_history, steps_log,
        time.time() - start_time,
    )
