"""
app.py
AI Search Visualizer - Streamlit frontend.

Run with:
    streamlit run app.py
"""

import os
import time

import pandas as pd
import streamlit as st

from core.grid_utils import load_map, validate_grid
from core.visualizer import grid_to_html, legend_html, result_to_log_text
from core.result_schema import ALGORITHM_TYPE
from algorithms import ALGORITHMS, UNINFORMED, INFORMED

# --------------------------------------------------------------------------- #
# Paths & page setup
# --------------------------------------------------------------------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data_test")
LOG_DIR = os.path.join(BASE_DIR, "logs")

st.set_page_config(
    page_title="AI Search Visualizer",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Styling - soft pink / blush / pastel, Pinterest-style but tidy
# --------------------------------------------------------------------------- #
CSS = """
<style>
:root{
  --blush:#FFF6FB; --rose:#FF8FB1; --plum:#b14d86; --lilac:#C9A7F0;
  --ink:#5a3f63; --soft:#6a4f7a;
}
.stApp{
  background: radial-gradient(1200px 500px at 10% -10%, #FFF0F7 0%, #FBF4FF 45%, #F7F7FF 100%);
}
/* Header */
.hero{
  background: linear-gradient(120deg,#FFB6D5 0%, #D9A7F0 55%, #B7C7FF 100%);
  border-radius:26px; padding:26px 30px; color:#3a2150;
  box-shadow:0 10px 30px rgba(200,120,170,0.25); margin-bottom:6px;
}
.hero h1{ margin:0; font-size:34px; font-weight:800; letter-spacing:.3px;}
.hero p{ margin:.35rem 0 0; font-size:15.5px; color:#4a2c5e; opacity:.92;}
.badge{
  display:inline-block; background:rgba(255,255,255,.55); color:#7a2e5c;
  padding:3px 12px; border-radius:999px; font-size:12.5px; font-weight:700;
  margin-top:10px; margin-right:6px;
}
/* Cards */
.card{
  background:#fff; border:1px solid #F6D9EC; border-radius:20px;
  padding:16px 18px; box-shadow:0 6px 18px rgba(200,120,170,0.10);
}
.metric{
  background:#fff; border:1px solid #F6D9EC; border-radius:18px;
  padding:14px 16px; text-align:center; box-shadow:0 4px 14px rgba(200,120,170,0.10);
}
.metric .label{ font-size:12.5px; color:var(--soft); font-weight:600;}
.metric .value{ font-size:24px; color:var(--plum); font-weight:800; margin-top:2px;}
.section-title{ color:var(--plum); font-weight:800; font-size:20px; margin:6px 0 10px;}
.note{
  background:#FFF7FC; border-left:4px solid var(--rose); border-radius:12px;
  padding:10px 14px; color:var(--soft); font-size:14px; margin:6px 0;
}
/* Sidebar */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#FFF0F7 0%, #F6EEFF 100%);
  border-right:1px solid #F3D9EC;
}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3{ color:var(--plum);}
/* Buttons */
.stButton>button{
  border-radius:14px; border:1px solid #F3C5DD; background:#fff; color:#a23a73;
  font-weight:700; padding:.5rem .8rem; transition:.15s;
}
.stButton>button:hover{ background:#FFE7F2; border-color:var(--rose); color:#8e2b60;}
/* Tabs */
.stTabs [data-baseweb="tab-list"]{ gap:6px;}
.stTabs [data-baseweb="tab"]{
  background:#fff; border:1px solid #F6D9EC; border-radius:14px 14px 0 0;
  padding:8px 16px; color:var(--soft); font-weight:700;
}
.stTabs [aria-selected="true"]{ background:#FFE7F2; color:var(--plum);}
/* Dataframe rounding */
[data-testid="stDataFrame"]{ border-radius:16px; overflow:hidden;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
      <h1>🌸 AI Search Visualizer</h1>
      <p>Weighted Grid Pathfinding with Uninformed and Informed Search Algorithms</p>
      <span class="badge">BFS · DFS · UCS · DLS · IDS</span>
      <span class="badge">Greedy · A*</span>
      <span class="badge">Manhattan heuristic</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
ss = st.session_state
ss.setdefault("single", None)      # {"result":..., "grid":..., "meta":...}
ss.setdefault("compare", None)     # {"results": {...}, "grid":..., "meta":...}


def list_maps():
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".txt"))


# --------------------------------------------------------------------------- #
# Sidebar controls
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("### 🎀 Controls")

    maps = list_maps()
    if not maps:
        st.error("No maps found in data_test/. Add a .txt grid map to continue.")
        st.stop()

    map_name = st.selectbox("🗺️ Map", maps, index=0)
    grid = load_map(os.path.join(DATA_DIR, map_name))
    rows, cols = len(grid), len(grid[0])
    st.caption(f"Grid size: {rows} × {cols}")

    algo_name = st.selectbox("🧭 Algorithm", list(ALGORITHMS.keys()), index=0)

    st.markdown("**📍 Start position**")
    sc1, sc2 = st.columns(2)
    start_r = int(sc1.number_input("Start row", 0, rows - 1, 0, key="sr"))
    start_c = int(sc2.number_input("Start col", 0, cols - 1, 0, key="sc"))

    st.markdown("**🎯 Goal position**")
    gc1, gc2 = st.columns(2)
    goal_r = int(gc1.number_input("Goal row", 0, rows - 1, rows - 1, key="gr"))
    goal_c = int(gc2.number_input("Goal col", 0, cols - 1, cols - 1, key="gc"))

    start, goal = (start_r, start_c), (goal_r, goal_c)

    depth_limit = int(
        st.number_input(
            "🪜 Depth limit (DLS / IDS)", min_value=0, max_value=300, value=20, step=1,
            help="DLS uses this as a hard cutoff. IDS uses it as the deepest level "
                 "it will try before giving up. Large maps may need a bigger value.",
        )
    )

    st.divider()
    run_one = st.button("▶️ Run Selected Algorithm", use_container_width=True)
    run_all = st.button("✨ Run All Algorithms", use_container_width=True)
    reset = st.button("🔄 Reset", use_container_width=True)

    # Validate up front so we can warn the user.
    valid, vmsg = validate_grid(grid, start, goal)
    if not valid:
        st.error(vmsg)

if reset:
    ss.single = None
    ss.compare = None
    st.rerun()


def run_single():
    res = ALGORITHMS[algo_name].run(grid, start, goal, depth_limit=depth_limit)
    ss.single = {
        "result": res,
        "grid": grid,
        "meta": {"map": map_name, "algo": algo_name, "start": start, "goal": goal,
                 "depth_limit": depth_limit},
    }


def run_compare():
    results = {}
    for name, mod in ALGORITHMS.items():
        results[name] = mod.run(grid, start, goal, depth_limit=depth_limit)
    ss.compare = {
        "results": results,
        "grid": grid,
        "meta": {"map": map_name, "start": start, "goal": goal,
                 "depth_limit": depth_limit},
    }


if run_one and valid:
    run_single()
if run_all and valid:
    run_compare()

# --------------------------------------------------------------------------- #
# Tabs
# --------------------------------------------------------------------------- #
tab_viz, tab_cmp, tab_about = st.tabs(["🗺️ Visualizer", "📊 Compare All", "📖 About"])


# ---- helpers for rendering ------------------------------------------------ #
def metric(col, label, value):
    col.markdown(
        f'<div class="metric"><div class="label">{label}</div>'
        f'<div class="value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def status_chip(found):
    if found:
        return '<span class="badge" style="background:#C7F0D8;color:#1f6b42;">✅ Path found</span>'
    return '<span class="badge" style="background:#FBD2D8;color:#9b2233;">❌ No path</span>'


# =========================================================================== #
# TAB 1 - VISUALIZER
# =========================================================================== #
with tab_viz:
    if ss.single is None:
        st.markdown(
            '<div class="note">Pick a map and an algorithm in the sidebar, then '
            'press <b>Run Selected Algorithm</b> to watch it search. 🌷</div>',
            unsafe_allow_html=True,
        )
        # Show a neutral preview of the current grid.
        st.markdown('<div class="section-title">Map preview</div>', unsafe_allow_html=True)
        pv1, pv2 = st.columns([3, 1])
        with pv1:
            st.markdown(grid_to_html(grid, start, goal), unsafe_allow_html=True)
        with pv2:
            st.markdown(legend_html(), unsafe_allow_html=True)
    else:
        data = ss.single
        res = data["result"]
        g = data["grid"]
        meta = data["meta"]

        st.markdown(
            f'<div class="section-title">{meta["algo"]} · {meta["map"]} '
            f'&nbsp;{status_chip(res["found"])}</div>',
            unsafe_allow_html=True,
        )

        m = st.columns(6)
        metric(m[0], "Found", "Yes" if res["found"] else "No")
        metric(m[1], "Cost", res["cost"] if res["cost"] is not None else "—")
        metric(m[2], "Path length", len(res["path"]) if res["path"] else 0)
        metric(m[3], "Expanded", res["expanded_nodes"])
        metric(m[4], "Generated", res["generated_nodes"])
        metric(m[5], "Time (ms)", f'{res["execution_time"]*1000:.2f}')

        st.write("")
        steps = res["steps_log"]
        left, right = st.columns([3, 1])

        with right:
            st.markdown(legend_html(), unsafe_allow_html=True)
            show_path = st.checkbox("Show final path overlay", value=True)

        with left:
            if steps:
                total = len(steps)
                idx = st.slider("Step", 1, total, total, help="Drag to replay the search.") - 1
                step = steps[idx]
                explored = res["explored_history"][idx] if idx < len(res["explored_history"]) else []
                frontier = res["frontier_history"][idx] if idx < len(res["frontier_history"]) else []
                current = step["current"]
                path = res["path"] if (show_path and idx == total - 1 and res["found"]) else \
                    (res["path"] if show_path and res["found"] else [])
                st.markdown(
                    grid_to_html(g, meta["start"], meta["goal"],
                                 explored=explored, frontier=frontier,
                                 path=path, current=current),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    grid_to_html(g, meta["start"], meta["goal"],
                                 path=res["path"] if res["found"] else []),
                    unsafe_allow_html=True,
                )

        # Step detail panel
        if steps:
            s = steps[idx]
            cutoff = " · ⚠️ cutoff" if s.get("cutoff") else ""
            st.markdown(
                f'<div class="card">'
                f'<b style="color:#b14d86;">Step {s["step"]} of {len(steps)}{cutoff}</b><br>'
                f'<b>Current:</b> {s["current"]} &nbsp;|&nbsp; '
                f'<b>Depth:</b> {s.get("depth", 0)} &nbsp;|&nbsp; '
                f'<b>Cost so far:</b> {s["cost_so_far"]}<br>'
                f'<b>Children:</b> {s["children"]}<br>'
                f'<b>Frontier ({len(s["frontier"])}):</b> {s["frontier"]}<br>'
                f'<b>Explored ({len(s["explored"])}):</b> {s["explored"]}'
                + (f'<br><i style="color:#8a5a1f;">{s["note"]}</i>' if s.get("note") else "")
                + '</div>',
                unsafe_allow_html=True,
            )

        st.write("")
        if res["found"]:
            st.success(f'Final path ({len(res["path"])} cells, total cost {res["cost"]}): '
                       f'{res["path"]}')
        else:
            st.warning(res["message"])

        # ---- Export log ---- #
        log_text = result_to_log_text(res, meta["map"], meta["start"], meta["goal"])
        safe_algo = res["algorithm"].replace("*", "star")
        log_name = f'{safe_algo}_{os.path.splitext(meta["map"])[0]}_log.txt'
        ecol1, ecol2 = st.columns([1, 3])
        with ecol1:
            if st.button("💾 Save log to logs/", use_container_width=True):
                os.makedirs(LOG_DIR, exist_ok=True)
                with open(os.path.join(LOG_DIR, log_name), "w", encoding="utf-8") as f:
                    f.write(log_text)
                st.toast(f"Saved logs/{log_name}", icon="💾")
        with ecol2:
            st.download_button("⬇️ Download log", log_text, file_name=log_name,
                               mime="text/plain", use_container_width=True)


# =========================================================================== #
# TAB 2 - COMPARE ALL
# =========================================================================== #
EXPLANATIONS = [
    "A* usually finds an optimal low-cost path while expanding fewer nodes than UCS, "
    "because the heuristic steers it toward the goal.",
    "UCS is optimal for any non-negative path costs, but with no heuristic it explores "
    "outward in every direction.",
    "Greedy is fast but not guaranteed to find the lowest-cost path, since it ignores "
    "the cost already paid.",
    "BFS is optimal only when every step costs the same; on weighted maps it can return "
    "a short path that is actually expensive.",
    "DFS may find a path quickly but it is typically neither shortest nor cheapest.",
    "DLS is DFS with a depth cutoff: it can miss a reachable goal if the limit is too "
    "small, which shows up as a cutoff.",
    "IDS finds the shallowest goal like BFS while using little memory, at the cost of "
    "re-exploring shallow levels many times.",
]

with tab_cmp:
    if ss.compare is None:
        st.markdown(
            '<div class="note">Press <b>Run All Algorithms</b> in the sidebar to compare '
            'every search strategy on the same map. 🌼</div>',
            unsafe_allow_html=True,
        )
    else:
        cdata = ss.compare
        meta = cdata["meta"]
        results = cdata["results"]
        st.markdown(
            f'<div class="section-title">Comparison · {meta["map"]} · '
            f'{meta["start"]} → {meta["goal"]} (depth limit {meta["depth_limit"]})</div>',
            unsafe_allow_html=True,
        )

        rows_data = []
        for name in ALGORITHMS.keys():
            r = results[name]
            rows_data.append({
                "Algorithm": name,
                "Type": ALGORITHM_TYPE[name],
                "Found": "✅" if r["found"] else "❌",
                "Cost": r["cost"] if r["cost"] is not None else "—",
                "Path length": len(r["path"]) if r["path"] else 0,
                "Expanded": r["expanded_nodes"],
                "Generated": r["generated_nodes"],
                "Time (ms)": round(r["execution_time"] * 1000, 3),
            })
        df = pd.DataFrame(rows_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Charts
        chart_df = df[df["Cost"] != "—"].copy()
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown('<b style="color:#b14d86;">Nodes expanded</b>', unsafe_allow_html=True)
            st.bar_chart(df.set_index("Algorithm")["Expanded"], color="#FF8FB1")
        with cc2:
            st.markdown('<b style="color:#b14d86;">Path cost</b>', unsafe_allow_html=True)
            if not chart_df.empty:
                st.bar_chart(chart_df.set_index("Algorithm")["Cost"], color="#C9A7F0")
            else:
                st.info("No solvable result to chart on this map.")

        st.markdown('<div class="section-title">What the numbers mean</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="card">'
            + "".join(f"🌷 {line}<br>" for line in EXPLANATIONS)
            + "</div>",
            unsafe_allow_html=True,
        )


# =========================================================================== #
# TAB 3 - ABOUT
# =========================================================================== #
with tab_about:
    st.markdown('<div class="section-title">About this project</div>', unsafe_allow_html=True)
    st.markdown(
        """
A robot moves on a weighted grid from a **start** cell to a **goal** cell, using only
four moves — **Up, Down, Left, Right** (no diagonals). Some cells are walls, and some
cost more to enter.

**Grid legend**

| Value | Meaning | Cost |
|------:|---------|-----:|
| `0` | normal path | 1 |
| `1` | wall / obstacle | impassable |
| `2` | difficult path | 3 |
| `3` | very difficult path | 5 |

**Heuristic** — Manhattan distance: `h(n) = |row − goal_row| + |col − goal_col|`

**Evaluation functions**

- UCS: `f(n) = g(n)`
- Greedy: `f(n) = h(n)`
- A*: `f(n) = g(n) + h(n)`

Start and goal are passed separately as `(row, col)` and are never written into the grid.
        """
    )
    st.markdown(legend_html(), unsafe_allow_html=True)
