"""
core/result_schema.py
A single source of truth for the dictionary every algorithm returns.

Using these helpers guarantees that BFS, DFS, UCS, DLS, IDS, Greedy and A*
all return *exactly* the same keys, which keeps the frontend and the
comparison table simple and robust.
"""

# Every result dict has exactly these keys, in this order.
RESULT_KEYS = [
    "algorithm",
    "found",
    "path",
    "cost",
    "expanded_nodes",
    "generated_nodes",
    "visited_order",
    "frontier_history",
    "explored_history",
    "steps_log",
    "execution_time",
    "message",
]

# Every steps_log entry has exactly these keys.
STEP_KEYS = [
    "step",
    "current",
    "children",
    "frontier",
    "explored",
    "cost_so_far",
    "depth",
    "cutoff",
    "note",
]

# Used by the frontend / comparison table to label algorithms.
ALGORITHM_TYPE = {
    "BFS": "Uninformed",
    "DFS": "Uninformed",
    "UCS": "Uninformed",
    "DLS": "Uninformed",
    "IDS": "Uninformed",
    "Greedy": "Informed",
    "A*": "Informed",
}


def new_step(step, current, children=None, frontier=None, explored=None,
             cost_so_far=0, depth=0, cutoff=False, note=""):
    """Build one standardized entry for steps_log."""
    return {
        "step": step,
        "current": current,
        "children": list(children) if children else [],
        "frontier": list(frontier) if frontier else [],
        "explored": list(explored) if explored else [],
        "cost_so_far": cost_so_far,
        "depth": depth,
        "cutoff": cutoff,
        "note": note,
    }


def make_result(algorithm, found, path=None, cost=None,
                expanded_nodes=0, generated_nodes=0,
                visited_order=None, frontier_history=None,
                explored_history=None, steps_log=None,
                execution_time=0.0, message=None):
    """Build a complete, schema-compliant result dictionary."""
    if message is None:
        message = "Goal found successfully." if found else "No path found."
    return {
        "algorithm": algorithm,
        "found": found,
        "path": list(path) if path else [],
        "cost": cost if found else None,
        "expanded_nodes": expanded_nodes,
        "generated_nodes": generated_nodes,
        "visited_order": list(visited_order) if visited_order else [],
        "frontier_history": list(frontier_history) if frontier_history else [],
        "explored_history": list(explored_history) if explored_history else [],
        "steps_log": list(steps_log) if steps_log else [],
        "execution_time": execution_time,
        "message": message,
    }


def validate_result(result):
    """Return (ok, message). Used by the test harness to enforce the schema."""
    missing = [k for k in RESULT_KEYS if k not in result]
    if missing:
        return False, f"Result is missing keys: {missing}"
    for i, step in enumerate(result["steps_log"]):
        step_missing = [k for k in STEP_KEYS if k not in step]
        if step_missing:
            return False, f"steps_log[{i}] is missing keys: {step_missing}"
    return True, "Result matches the schema."
