"""
main.py
Command-line runner for the AI Search Visualizer.

Use this to run any algorithm (or all of them) on any map straight from a
terminal, without launching the Streamlit app. Useful for quick checks and for
generating log files.

Examples
--------
    python main.py                                   # A* on map_easy
    python main.py --map map_weighted.txt --algo all # every algorithm
    python main.py --algo DLS --depth-limit 12 --save-log
    python main.py --all-maps --algo all             # full sweep
"""

import os
import argparse

from core.grid_utils import load_map, validate_grid
from core.result_schema import ALGORITHM_TYPE
from core.visualizer import result_to_log_text
from algorithms import ALGORITHMS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data_test")
LOG_DIR = os.path.join(BASE_DIR, "logs")


def parse_point(text, fallback):
    if text is None:
        return fallback
    r, c = text.replace("(", "").replace(")", "").split(",")
    return (int(r), int(c))


def print_grid(grid):
    for row in grid:
        print("  " + " ".join(str(v) for v in row))


def print_result(res):
    type_tag = ALGORITHM_TYPE.get(res["algorithm"], "")
    print(f"--- {res['algorithm']} ({type_tag}) ---")
    print(f"  Found          : {res['found']}")
    print(f"  Cost           : {res['cost']}")
    print(f"  Path length    : {len(res['path'])}")
    print(f"  Expanded nodes : {res['expanded_nodes']}")
    print(f"  Generated nodes: {res['generated_nodes']}")
    print(f"  Execution time : {res['execution_time']*1000:.3f} ms")
    print(f"  Message        : {res['message']}")
    if res["found"]:
        print(f"  Path           : {res['path']}")


def save_log(res, map_name, start, goal):
    os.makedirs(LOG_DIR, exist_ok=True)
    safe = res["algorithm"].replace("*", "star")
    name = f"{safe}_{os.path.splitext(map_name)[0]}_log.txt"
    path = os.path.join(LOG_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(result_to_log_text(res, map_name, start, goal))
    print(f"  log saved      : logs/{name}")


def run_on_map(map_name, algo, start_text, goal_text, depth_limit, save):
    grid = load_map(os.path.join(DATA_DIR, map_name))
    rows, cols = len(grid), len(grid[0])
    start = parse_point(start_text, (0, 0))
    goal = parse_point(goal_text, (rows - 1, cols - 1))

    print("=" * 60)
    print(f"MAP: {map_name}  ({rows}x{cols})   start={start}  goal={goal}")
    print("=" * 60)
    print_grid(grid)
    print()

    ok, msg = validate_grid(grid, start, goal)
    if not ok:
        print(f"  Invalid setup: {msg}")
        return

    names = list(ALGORITHMS.keys()) if algo == "all" else [algo]
    for name in names:
        res = ALGORITHMS[name].run(grid, start, goal, depth_limit=depth_limit)
        print_result(res)
        if save:
            save_log(res, map_name, start, goal)
        print()


def main():
    parser = argparse.ArgumentParser(description="AI Search Visualizer CLI runner")
    parser.add_argument("--map", default="map_easy.txt", help="map filename in data_test/")
    parser.add_argument("--algo", default="A*",
                        help="algorithm name (BFS, DFS, UCS, DLS, IDS, Greedy, A*) or 'all'")
    parser.add_argument("--start", default=None, help="start as row,col (default 0,0)")
    parser.add_argument("--goal", default=None, help="goal as row,col (default bottom-right)")
    parser.add_argument("--depth-limit", type=int, default=20, help="for DLS / IDS")
    parser.add_argument("--save-log", action="store_true", help="write logs to logs/")
    parser.add_argument("--all-maps", action="store_true", help="run on every map in data_test/")
    args = parser.parse_args()

    if args.algo != "all" and args.algo not in ALGORITHMS:
        parser.error(f"Unknown algorithm '{args.algo}'. "
                     f"Choose from: {', '.join(ALGORITHMS)} or 'all'.")

    if args.all_maps:
        maps = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".txt"))
        for m in maps:
            run_on_map(m, args.algo, args.start, args.goal, args.depth_limit, args.save_log)
    else:
        run_on_map(args.map, args.algo, args.start, args.goal, args.depth_limit, args.save_log)


if __name__ == "__main__":
    main()
