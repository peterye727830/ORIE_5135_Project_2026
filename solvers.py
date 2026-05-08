# --- START OF FILE solvers.py ---
import json
import time
import gurobipy as gp
from gurobipy import GRB
import networkx as nx


# 1. model 1a
def solve_natural_formulation(json_file_path, time_limit):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    m, n, R, r, edges = data['m'], data['n'], data['R'], data['r'], data['edges']
    V, T = list(range(m)), list(range(n))
    E = [(u - 1, v - 1) for u, v in edges]
    model = gp.Model("Natural_1a")
    model.setParam('OutputFlag', 0)
    x = model.addVars(V, T, vtype=GRB.BINARY)
    y = model.addVars(T, vtype=GRB.BINARY)
    model.setObjective(gp.quicksum(y[j] for j in T), GRB.MINIMIZE)
    for i in V: model.addConstr(gp.quicksum(x[i, j] for j in T) == 1)
    for j in T: model.addConstr(gp.quicksum(r[i] * x[i, j] for i in V) <= R * y[j])
    for u, v in E:
        for j in T: model.addConstr(x[u, j] + x[v, j] <= y[j])
    for j in range(n - 1): model.addConstr(y[j] >= y[j + 1])

    model.update()

    lp_relaxation_value = float('nan')
    try:
        lp_model = model.relax()
        lp_model.optimize()
        if lp_model.status == GRB.OPTIMAL: lp_relaxation_value = lp_model.ObjVal
    except gp.GurobiError:
        pass

    model.setParam('TimeLimit', time_limit)
    model.optimize()
    return {
        "formulation": "1a_Natural", "lp_relaxation": lp_relaxation_value,
        "obj_val": model.ObjVal if model.SolCount > 0 else -1,
        "node_count": model.NodeCount, "solve_time": model.Runtime, "is_optimal": model.status == GRB.OPTIMAL
    }


# 2. model 1b
def solve_clique_formulation(json_file_path, time_limit):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    m, n, R, r, edges = data['m'], data['n'], data['R'], data['r'], data['edges']
    V, T = list(range(m)), list(range(n))
    E = [(u - 1, v - 1) for u, v in edges]
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)
    maximal_cliques = list(nx.find_cliques(G))
    model = gp.Model("Clique_1b")
    model.setParam('OutputFlag', 0)
    x = model.addVars(V, T, vtype=GRB.BINARY)
    y = model.addVars(T, vtype=GRB.BINARY)
    model.setObjective(gp.quicksum(y[j] for j in T), GRB.MINIMIZE)
    for i in V: model.addConstr(gp.quicksum(x[i, j] for j in T) == 1)
    for j in T: model.addConstr(gp.quicksum(r[i] * x[i, j] for i in V) <= R * y[j])
    for C in maximal_cliques:
        for j in T: model.addConstr(gp.quicksum(x[i, j] for i in C) <= y[j])
    for j in range(n - 1): model.addConstr(y[j] >= y[j + 1])

    model.update()

    lp_relaxation_value = float('nan')
    try:
        lp_model = model.relax()
        lp_model.optimize()
        if lp_model.status == GRB.OPTIMAL: lp_relaxation_value = lp_model.ObjVal
    except gp.GurobiError:
        pass

    model.setParam('TimeLimit', time_limit)
    model.optimize()
    return {
        "formulation": "1b_Clique", "lp_relaxation": lp_relaxation_value,
        "obj_val": model.ObjVal if model.SolCount > 0 else -1,
        "node_count": model.NodeCount, "solve_time": model.Runtime, "is_optimal": model.status == GRB.OPTIMAL
    }


# 3. model 2a
def solve_extended_formulation(json_file_path, time_limit):
    start_time = time.time()
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    m, R, r, edges = data['m'], data['R'], data['r'], data['edges']
    V = list(range(m))
    adj = {i: set() for i in V}
    for u, v in edges:
        adj[u - 1].add(v - 1)
        adj[v - 1].add(u - 1)

    feasible_groupings = []

    def dfs(start_idx, current_group, current_req):
        if time.time() - start_time > time_limit: return
        if current_group: feasible_groupings.append(list(current_group))
        for i in range(start_idx, m):
            if current_req + r[i] > R: continue
            is_independent = True
            for j in current_group:
                if j in adj[i]:
                    is_independent = False
                    break
            if is_independent:
                current_group.append(i)
                dfs(i + 1, current_group, current_req + r[i])
                current_group.pop()

    dfs(0, [], 0)

    gurobi_time_limit = time_limit - (time.time() - start_time)
    if gurobi_time_limit <= 0:
        return {"formulation": "2_Extended", "lp_relaxation": -1, "obj_val": -1, "node_count": -1,
                "solve_time": time_limit, "is_optimal": False}

    model = gp.Model("Extended_2")
    model.setParam('OutputFlag', 0)
    lam = model.addVars(len(feasible_groupings), vtype=GRB.BINARY)
    model.setObjective(gp.quicksum(lam[k] for k in range(len(feasible_groupings))), GRB.MINIMIZE)
    for i in V: model.addConstr(gp.quicksum(lam[k] for k, S in enumerate(feasible_groupings) if i in S) == 1)

    model.update()

    lp_relaxation_value = float('nan')
    try:
        lp_model = model.relax()
        lp_model.optimize()
        if lp_model.status == GRB.OPTIMAL: lp_relaxation_value = lp_model.ObjVal
    except gp.GurobiError:
        pass

    model.setParam('TimeLimit', gurobi_time_limit)
    model.optimize()
    return {
        "formulation": "2_Extended", "lp_relaxation": lp_relaxation_value,
        "obj_val": model.ObjVal if model.SolCount > 0 else -1,
        "node_count": model.NodeCount, "solve_time": time.time() - start_time, "is_optimal": model.status == GRB.OPTIMAL
    }