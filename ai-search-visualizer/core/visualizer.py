"""
core/visualizer.py
Presentation helpers for the Streamlit frontend.

This module only builds strings (HTML and log text); it does not call Streamlit,
so it stays easy to test and reuse.
"""

# (background, text) colour for each visual role. Pastel / blush palette.
PALETTE = {
    "start":    ("#C9A7F0", "#3a2a55"),   # lavender-purple
    "goal":     ("#FF8FB1", "#5a1f33"),   # rose
    "current":  ("#FF4D88", "#ffffff"),   # vivid pink
    "path":     ("#A8E6CF", "#1f5c3d"),   # mint green
    "wall":     ("#4A4458", "#4A4458"),   # dark gray-violet
    "frontier": ("#FFF1A8", "#7a6a1f"),   # soft yellow
    "explored": ("#E7D9F5", "#6a4f8a"),   # soft lavender
    "weight2":  ("#BFE3F5", "#1f4b66"),   # light blue  (value 2 -> cost 3)
    "weight3":  ("#FFD9A8", "#8a5a1f"),   # light orange(value 3 -> cost 5)
    "normal":   ("#FFFFFF", "#c2b3d6"),   # white
}

# Order matters: legend reads top to bottom in the UI.
LEGEND = [
    ("start", "Start"),
    ("goal", "Goal"),
    ("current", "Current node"),
    ("path", "Final path"),
    ("frontier", "Frontier"),
    ("explored", "Explored"),
    ("weight2", "Difficult · cost 3"),
    ("weight3", "Very difficult · cost 5"),
    ("normal", "Normal · cost 1"),
    ("wall", "Wall"),
]


def _as_set(x):
    return set(x) if x else set()


def grid_to_html(grid, start, goal, explored=None, frontier=None,
                 path=None, current=None, cell_px=46):
    """Render the grid as a self-contained HTML block.

    explored / frontier / path may be lists or sets of (row, col).
    current is a single (row, col) or None.
    """
    explored = _as_set(explored)
    frontier = _as_set(frontier)
    path = _as_set(path)

    rows, cols = len(grid), len(grid[0])
    cells = []
    for r in range(rows):
        for c in range(cols):
            value = grid[r][c]
            node = (r, c)
            label = ""

            # Resolve the visual role by priority.
            if node == start:
                role, label = "start", "🤖"
            elif node == goal:
                role, label = "goal", "🎯"
            elif node == current:
                role, label = "current", "✦"
            elif node in path:
                role = "path"
            elif value == 1:
                role = "wall"
            elif node in frontier:
                role = "frontier"
            elif node in explored:
                role = "explored"
            elif value == 2:
                role, label = "weight2", "3"
            elif value == 3:
                role, label = "weight3", "5"
            else:
                role = "normal"

            # Keep the cost digit visible on weighted cells even when overlaid.
            if not label and value in (2, 3) and role in ("explored", "frontier", "path"):
                label = "3" if value == 2 else "5"

            bg, fg = PALETTE[role]
            border = "2px solid #FF4D88" if role == "current" else "1px solid #F3E6F5"
            cells.append(
                f'<div style="background:{bg};color:{fg};'
                f'display:flex;align-items:center;justify-content:center;'
                f'height:{cell_px}px;border-radius:12px;border:{border};'
                f'font-size:{int(cell_px*0.42)}px;font-weight:700;'
                f'box-shadow:0 1px 2px rgba(120,80,140,0.10);">{label}</div>'
            )

    grid_css = (
        f'display:grid;gap:6px;'
        f'grid-template-columns:repeat({cols}, {cell_px}px);'
        f'padding:16px;background:#FFF6FB;border-radius:22px;'
        f'border:1px solid #F6D9EC;box-shadow:0 8px 24px rgba(200,120,170,0.12);'
        f'width:max-content;'
    )
    return f'<div style="{grid_css}">{"".join(cells)}</div>'


def legend_html():
    """Small colour legend matching grid_to_html."""
    items = []
    for role, text in LEGEND:
        bg, _ = PALETTE[role]
        border = "1px solid #d9c7e8" if role == "normal" else "none"
        items.append(
            f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
            f'<span style="width:18px;height:18px;border-radius:6px;'
            f'background:{bg};border:{border};display:inline-block;"></span>'
            f'<span style="font-size:13px;color:#6a4f7a;">{text}</span></div>'
        )
    return (
        '<div style="background:#FFFFFF;border:1px solid #F6D9EC;border-radius:18px;'
        'padding:14px 18px;box-shadow:0 4px 14px rgba(200,120,170,0.10);">'
        '<div style="font-weight:700;color:#b14d86;margin-bottom:8px;">Legend</div>'
        + "".join(items) + "</div>"
    )


def result_to_log_text(result, map_name, start, goal):
    """Build a human-readable, step-by-step log for export."""
    lines = []
    lines.append("=" * 64)
    lines.append(f"  AI Search Visualizer - run log")
    lines.append("=" * 64)
    lines.append(f"Algorithm      : {result['algorithm']}")
    lines.append(f"Map            : {map_name}")
    lines.append(f"Start / Goal   : {start} -> {goal}")
    lines.append(f"Found          : {result['found']}")
    lines.append(f"Path cost      : {result['cost']}")
    lines.append(f"Path length    : {len(result['path'])} cells")
    lines.append(f"Expanded nodes : {result['expanded_nodes']}")
    lines.append(f"Generated nodes: {result['generated_nodes']}")
    lines.append(f"Execution time : {result['execution_time']:.6f} s")
    lines.append(f"Message        : {result['message']}")
    lines.append(f"Path           : {result['path']}")
    lines.append("-" * 64)
    lines.append("Step-by-step trace:")
    lines.append("-" * 64)
    for s in result["steps_log"]:
        tag = " [CUTOFF]" if s.get("cutoff") else ""
        note = f"  // {s['note']}" if s.get("note") else ""
        lines.append(
            f"step {s['step']:>4} | current {str(s['current']):>8} | "
            f"depth {s.get('depth', 0):>3} | cost {s['cost_so_far']:>4} | "
            f"children {s['children']}{tag}{note}"
        )
        lines.append(
            f"           frontier({len(s['frontier'])}): {s['frontier']}"
        )
    lines.append("=" * 64)
    return "\n".join(lines)
