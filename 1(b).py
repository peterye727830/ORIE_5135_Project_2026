import json
import gurobipy as gp
from gurobipy import GRB
import networkx as nx  # 新增：导入网络图分析库


def solve_clique_formulation(json_file_path):
    # 1. Read data (identical to 1a)
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    m, n, R = data['m'], data['n'], data['R']
    r, edges = data['r'], data['edges']

    V = list(range(m))
    T = list(range(n))
    E = [(u - 1, v - 1) for u, v in edges]

    # ---------------------------------------------------------
    # 2. Core new logic: build conflict graph and find all maximal cliques
    # ---------------------------------------------------------
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)

    # Find all maximal cliques; returns a list where each element is a clique (also a list)
    # Example: [[0, 1], [1, 2], [0, 3]]
    maximal_cliques = list(nx.find_cliques(G))
    # print(f"Maximal cliques found: {maximal_cliques}")  # Uncomment to inspect

    # 3. Create Gurobi model
    model = gp.Model("Exam_Scheduling_Clique")
    # model.setParam('OutputFlag', 0)  # Optional: suppress solver output

    # 4. Create decision variables
    x = model.addVars(V, T, vtype=GRB.BINARY, name="x")
    y = model.addVars(T, vtype=GRB.BINARY, name="y")

    # 5. Objective function
    model.setObjective(gp.quicksum(y[j] for j in T), GRB.MINIMIZE)

    # 6. Add constraints
    # (1) Assignment constraint (unchanged)
    for i in V:
        model.addConstr(gp.quicksum(x[i, j] for j in T) == 1, name=f"Assign_{i}")

    # (2) Capacity and linking constraint (unchanged)
    for j in T:
        model.addConstr(
            gp.quicksum(r[i] * x[i, j] for i in V) <= R * y[j],
            name=f"Capacity_{j}"
        )

    # ---------------------------------------------------------
    # (3) Strengthened conflict constraints (clique inequalities)
    # Replace the original edge constraints with maximal clique constraints
    # ---------------------------------------------------------
    for clique_idx, C in enumerate(maximal_cliques):
        for j in T:
            model.addConstr(
                gp.quicksum(x[i, j] for i in C) <= y[j],
                name=f"Clique_{clique_idx}_{j}"
            )

    # Symmetry breaking
    for j in range(n - 1):
        model.addConstr(y[j] >= y[j + 1], name=f"Symmetry_{j}")

    # 7. Solve
    model.setParam('TimeLimit', 120)
    model.optimize()

    # 8. Print results
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        print(f"\n--- 1(b) Clique-Strengthened Results ---")
        print(f"Optimal objective: {model.ObjVal}")
        print(f"B&B nodes explored: {model.NodeCount}")
        print(f"Solve time: {model.Runtime:.2f} seconds")
        for j in T:
            if y[j].x > 0.5:  # floating point comparison for y[j] == 1
                assigned_exams = [i + 1 for i in V if x[i, j].x > 0.5]  # convert back to 1-based
                print(f"Time slot {j + 1}: Exams {assigned_exams} (proctors used: {sum(r[i - 1] for i in assigned_exams)}/{R})")
    else:
        print("No feasible solution found.")


# Test code 
# create a test_data.json just for testing
solve_clique_formulation('test_data.json')