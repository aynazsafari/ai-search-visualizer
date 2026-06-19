"""
core/grid_utils.py
Shared helper functions used by every search algorithm.

Grid legend
-----------
0 = normal path      -> cost 1
1 = wall / obstacle  -> not passable
2 = difficult path   -> cost 3
3 = very difficult   -> cost 5

Coordinates are always (row, col). Movement is 4-directional only:
Up, Down, Left, Right (no diagonals).
"""

import os

# Fixed move order keeps every algorithm's tie-breaking deterministic.
MOVES = [("Up", -1, 0), ("Down", 1, 0), ("Left", 0, -1), ("Right", 0, 1)]

# Movement cost of *entering* a cell. A wall (1) has no cost (it is impassable).
CELL_COSTS = {0: 1, 2: 3, 3: 5}


def load_map(file_path):
    """Read a whitespace-separated integer grid from a text file.

    Returns a list of lists of ints. Raises FileNotFoundError if missing.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Map file not found: {file_path}")

    grid = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            tokens = line.strip().split()
            if tokens:
                grid.append([int(token) for token in tokens])
    return grid


def cell_cost(value):
    """Return the cost of entering a cell, or None if it is a wall/unknown."""
    return CELL_COSTS.get(value, None)


def manhattan_distance(node, goal):
    """Admissible heuristic for a 4-connected grid.

    h(n) = |row - goal_row| + |col - goal_col|
    """
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])


def get_neighbors(grid, node):
    """Return passable in-bounds neighbours in Up, Down, Left, Right order."""
    rows, cols = len(grid), len(grid[0])
    r, c = node
    neighbors = []
    for _, dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
            neighbors.append((nr, nc))
    return neighbors


def reconstruct_path(parent, start, goal):
    """Walk the parent pointers from goal back to start and return the path."""
    if goal not in parent:
        return []
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    # Guard against a broken chain that does not actually start at `start`.
    if path and path[0] != start:
        return []
    return path


def validate_grid(grid, start, goal):
    """Sanity-check a grid plus its start/goal.

    Returns (ok: bool, message: str).
    """
    if not grid or not grid[0]:
        return False, "Grid is empty."

    cols = len(grid[0])
    for row in grid:
        if len(row) != cols:
            return False, "Grid rows have inconsistent lengths."

    rows = len(grid)
    for label, (r, c) in (("Start", start), ("Goal", goal)):
        if not (0 <= r < rows and 0 <= c < cols):
            return False, f"{label} {(r, c)} is out of bounds for a {rows}x{cols} grid."
        if grid[r][c] == 1:
            return False, f"{label} {(r, c)} sits on a wall and is not passable."

    return True, "Grid is valid."
