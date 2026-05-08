# ORIE 5135 Project — Exam Scheduling

Spring 2026 final project for ORIE 5135. The task is to schedule a set of exams into
the smallest number of time slots, subject to a per-slot proctor budget and pairwise
student-conflict constraints encoded as a graph. Three integer programming
formulations are implemented and compared:

1. A **natural ILP** with one binary variable per (exam, slot) pair.
2. A **clique-strengthened ILP** that replaces pairwise conflict constraints with
   maximal-clique inequalities.
3. An **extended (set-partitioning) formulation** with one variable per feasible
   grouping of exams that can share a slot.

Each formulation is built and solved with Gurobi via `gurobipy`, on the two provided
datasets.

## Repository layout

```
.
├── main.tex                     LaTeX source of the writeup
├── main.pdf                     Compiled writeup (problem formulations + Q2b/Q3 discussion)
├── solvers.py                   Canonical implementations of all three formulations
├── main_3(a).py                 Driver: runs all three formulations on Dataset 1 (120s limit)
├── main_3(b).py                 Driver: runs Formulations 1a and 1b on Dataset 2 (600s limit)
├── 1(a).py                      Standalone walkthrough of Formulation 1a on test_data.json
├── 1(b).py                      Standalone walkthrough of Formulation 1b on test_data.json
├── 2(a).py                      Standalone walkthrough of Formulation 2 on test_data.json
├── test_data.json               Small toy instance used by the three standalone scripts
├── dataset1/                    Ten instances (m = 35..75) with 120s solve budget
├── dataset2/                    Nine larger instances (m = 80..90) with 600s solve budget
├── results_3(a).csv             Raw per-instance results that back Table 1 in the writeup
├── results_3(b).csv             Raw per-instance results that back Table 2 in the writeup
└── ORIE_5135_Project_2026.pdf   Assignment PDF (for reference)
```

## How to reproduce the results

Requirements: Python 3, `gurobipy` (with a valid Gurobi license), `pandas`, and
`networkx`.

```bash
pip install gurobipy pandas networkx
```

Then from the repository root:

```bash
python "main_3(a).py"      # writes results_3(a).csv
python "main_3(b).py"      # writes results_3(b).csv
```

Each driver iterates over its dataset, solves every instance with the relevant
formulations, and saves a per-row CSV containing the instance name, formulation,
optimality status, objective value, root LP relaxation value, branch-and-bound node
count, and wall-clock solve time.

## File-by-file notes

### `solvers.py`
The production library. Exposes three functions used by the experiment drivers:

- `solve_natural_formulation(json_path, time_limit)` — Formulation 1a.
- `solve_clique_formulation(json_path, time_limit)` — Formulation 1b. Maximal cliques
  in the conflict graph are enumerated with `networkx.find_cliques`.
- `solve_extended_formulation(json_path, time_limit)` — Formulation 2. Feasible
  groupings (independent sets of the conflict graph that also satisfy the proctor
  capacity) are enumerated by recursive DFS, then a set-partitioning ILP is built
  over them.

Each function records the LP relaxation value (via `model.relax()`) before the
integer solve and returns a dict with keys `formulation`, `lp_relaxation`,
`obj_val`, `node_count`, `solve_time`, `is_optimal`.

### `main_3(a).py`, `main_3(b).py`
Experiment drivers. They list the JSON instances in their respective dataset folder,
call the relevant solvers in `solvers.py` with the assignment-mandated time limit
(120s for Dataset 1, 600s for Dataset 2), assemble a `pandas.DataFrame`, and write it
to `results_3(a).csv` / `results_3(b).csv`.

### `1(a).py`, `1(b).py`, `2(a).py`
Standalone scripts that build each formulation on `test_data.json` and print a
human-readable schedule. They are intended as small, self-contained illustrations of
the three formulations and are not used to produce the Q3 numbers — the experiments
import everything from `solvers.py`.

### `dataset1/`, `dataset2/`
Each instance is a JSON file with fields `m` (number of exams), `n` (number of
available time slots), `R` (proctor budget per slot), `r` (list of proctor
requirements), and `edges` (list of conflicting exam pairs). The accompanying
`_params.csv` and `_edges.csv` files mirror the same data in tabular form.

### `results_3(a).csv`, `results_3(b).csv`
Raw outputs that back the two tables in the writeup. One row per (instance,
formulation) pair, columns: `instance`, `formulation`, `is_optimal`, `obj_val`,
`lp_relaxation`, `node_count`, `solve_time`.

### `main.tex`, `main.pdf`
The writeup. Contains the three problem formulations (Sections 1 and 2), the
set-covering vs.\ set-partitioning discussion (Section 4), and the computational
experiments and analysis on both datasets (Section 5).
