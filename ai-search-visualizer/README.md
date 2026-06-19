<div align="center">

<br/>

# 🌸 AI Path Compass — Search Algorithm Visualizer

**Watch AI think. Step by step. In real time.**

[![Python](https://img.shields.io/badge/Python-3.10+-ff69b4?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-c77dff?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Algorithms](https://img.shields.io/badge/Algorithms-7_Search_Methods-ffb3d1?style=flat-square)](#-algorithms)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4a7c3?style=flat-square)](LICENSE)

*An interactive visualizer for 7 classical AI search algorithms on weighted grids — with a pink aesthetic.*

<br/>

</div>

---
## Project Screenshot

<img width="1868" height="902" alt="Dashboard" src="https://github.com/user-attachments/assets/4e98eac6-a76c-4418-b157-0b9475abd891" />



## 🧠 What Is AI Path Compass?

**AI Path Compass** is a Streamlit application (+ CLI runner) that brings search algorithms to life.
Load a grid map, pick an algorithm, hit **Run** — and watch the frontier expand node by node,
comparing metrics like cost, expanded nodes, and execution time across methods side by side.

> Built for AI coursework, portfolio showcases, and anyone who learns better by *seeing* it happen.

---

## 🔮 Algorithms

### Uninformed Search

| Algorithm | Completeness | Optimality | Time | Space |
|---|---|---|---|---|
| **BFS** — Breadth-First Search | ✅ Yes | ✅ Yes (unit cost) | O(b^d) | O(b^d) |
| **DFS** — Depth-First Search | ⚠️ Finite graphs | ❌ No | O(b^m) | O(bm) |
| **UCS** — Uniform-Cost Search | ✅ Yes | ✅ Yes | O(b^(C*/ε)) | O(b^(C*/ε)) |
| **DLS** — Depth-Limited Search | ⚠️ If d ≤ limit | ❌ No | O(b^l) | O(bl) |
| **IDS** — Iterative Deepening | ✅ Yes | ✅ Yes (unit cost) | O(b^d) | O(bd) |

### Informed Search

| Algorithm | Heuristic | Optimality | Notes |
|---|---|---|---|
| **Greedy** Best-First | Manhattan distance | ❌ No | Fast, not always optimal |
| **A\*** Search | g(n) + h(n) | ✅ Yes | Best of both worlds |

---

## ✨ Features

| 💫 Feature | Description |
|---|---|
| **Interactive Grid** | Load prebuilt maps or design your own test cases |
| **Step-by-step Playback** | Pause and inspect every expansion step |
| **Side-by-side Comparison** | Run all 7 algorithms and compare metrics in one table |
| **Weighted Cells** | Normal (cost 1), difficult (cost 3), very difficult (cost 5) |
| **Log Export** | Save structured run logs to `logs/` via the CLI |
| **Aesthetic UI** | Soft blush-pink sidebar + gradient headers |
| **CLI Runner** | Headless mode for scripts, CI, and log generation |

---

## 🛠️ Tech Stack

```
Language      →  Python 3.10+
UI Framework  →  Streamlit  (interactive web app)
Data Layer    →  Pandas  (metrics tables, comparison views)
Algorithms    →  Pure Python  (heapq, collections.deque — no external deps)
Maps          →  Text files  (whitespace-separated integer grids)
Logs          →  Plain text  (structured, UTF-8)
```

---

## 📁 Project Structure

```
ai-search-visualizer/
│
├── app.py                  ← Streamlit frontend (main entry point)
├── main.py                 ← CLI runner (headless, log-friendly)
│
├── algorithms/             ← One file per search algorithm
│   ├── __init__.py         ← Registry: ALGORITHMS, UNINFORMED, INFORMED
│   ├── astar.py            ← A* (f = g + h, Manhattan heuristic)
│   ├── bfs.py              ← Breadth-First Search
│   ├── dfs.py              ← Depth-First Search
│   ├── dls.py              ← Depth-Limited Search
│   ├── greedy.py           ← Greedy Best-First Search
│   ├── ids.py              ← Iterative Deepening Search
│   └── ucs.py              ← Uniform-Cost Search
│
├── core/                   ← Shared utilities
│   ├── __init__.py
│   ├── grid_utils.py       ← Map loading, neighbours, costs, Manhattan h(n)
│   ├── result_schema.py    ← Unified result dict schema for all algorithms
│   └── visualizer.py       ← HTML grid rendering + log text formatter
│
├── data_test/              ← Built-in test maps
│   ├── map_easy.txt
│   ├── map_medium.txt
│   ├── map_hard.txt
│   ├── map_weighted.txt
│   └── map_no_path.txt
│
├── logs/                   ← Auto-generated run logs (.gitkeep keeps folder)
│   └── .gitkeep
│
├── docs/                   ← Project report (PDF / HTML)
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1 · Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-search-visualizer.git
cd ai-search-visualizer
```

### 2 · Create & activate a virtual environment *(recommended)*

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4a · Launch the Streamlit app

```bash
streamlit run app.py
```

> 🌐 Opens at `http://localhost:8501`

### 4b · Or use the CLI runner

```bash
# A* on the default easy map
python main.py

# Run every algorithm on the weighted map and save logs
python main.py --map map_weighted.txt --algo all --save-log

# DLS with a custom depth limit
python main.py --algo DLS --depth-limit 12

# Full benchmark sweep (all maps × all algorithms)
python main.py --all-maps --algo all --save-log
```

---

## 🗺️ Grid Legend

```
0 = open path         cost: 1   (white)
1 = wall / obstacle   cost: ∞   (blocked)
2 = difficult terrain cost: 3   (soft pink)
3 = very difficult    cost: 5   (deep rose)
S = start             ───────   (green)
G = goal              ───────   (gold)
```

---

## 📊 Metrics Tracked Per Run

| Metric | Description |
|---|---|
| `found` | Was a path found? |
| `cost` | Total path cost (respects terrain weights) |
| `path_length` | Number of cells in the solution path |
| `expanded_nodes` | Nodes popped from frontier |
| `generated_nodes` | Nodes ever added to frontier |
| `execution_time` | Wall-clock runtime in milliseconds |

---

## 🔮 Roadmap

- [ ] 🖱️ Drag-to-draw custom grids in the browser
- [ ] 📈 Animated node-expansion playback with speed control
- [ ] 🗂️ Bidirectional A* and Beam Search additions
- [ ] 📤 Export comparison results as PDF report
- [ ] 🌐 Deploy to Streamlit Community Cloud (one-click share)

---

## 🤝 Contributing

```bash
# Fork → clone → branch
git checkout -b feature/new-algorithm

# Implement your algorithm following the result_schema
# Then open a Pull Request 💗
```

All algorithms must expose a single:

```python
def run(grid, start, goal, **kwargs) -> dict:
    ...
```

and return the schema defined in `core/result_schema.py`.

---

## 📄 License

Distributed under the **MIT License** — free to use, adapt, and share.


---

<div align="center">

*Made with 🌸 curiosity and clean Python*

</div>
