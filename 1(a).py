import json
import gurobipy as gp
from gurobipy import GRB


def solve_natural_formulation(json_file_path):
    # 1. Read the data
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    m = data['m']       # number of exams
    n = data['n']       # number of available time slots
    R = data['R']       # proctor budget per slot
    r = data['r']       # list of proctor requirements for each exam
    edges = data['edges']  # list of conflicting exam pairs
    V = list(range(m))   # exam indices: 0 to m-1
    T = list(range(n))   # time slot indices: 0 to n-1
    # The JSON uses 1-based indices, convert edges to 0-based
    E = [(u - 1, v - 1) for u, v in edges]

    model = gp.Model("Exam_Scheduling_Natural")

    # x[i, j] = 1 if exam i is assigned to time slot j
    x = model.addVars(V, T, vtype=GRB.BINARY, name="x")
    # y[j] = 1 if time slot j is used
    y = model.addVars(T, vtype=GRB.BINARY, name="y")

    model.setObjective(gp.quicksum(y[j] for j in T), GRB.MINIMIZE)

    for i in V:
        model.addConstr(gp.quicksum(x[i, j] for j in T) == 1, name=f"Assign_{i}")

    for j in T:
        model.addConstr(
            gp.quicksum(r[i] * x[i, j] for i in V) <= R * y[j],
            name=f"Capacity_{j}")

    for u, v in E:
        for j in T:
            model.addConstr(
                x[u, j] + x[v, j] <= y[j],
                name=f"Conflict_{u}_{v}_{j}")

    # Since time slots are interchangeable, without this the solver wastes time exploring equivalent solutions that just shuffle which slot number is used.
     # Symmetry breaking
    
    for j in range(n - 1):
        model.addConstr(y[j] >= y[j + 1], name=f"Symmetry_{j}")

    model.setParam('TimeLimit', 120)
    model.optimize()

    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        print(f"\n--- Results ---")
        print(f"Optimal objective (number of time slots used): {model.ObjVal}")
        print(f"B&B nodes explored: {model.NodeCount}")
        print(f"Solve time: {model.Runtime:.2f} seconds")

        for j in T:
            if y[j].x > 0.5:  # floating point comparison for y[j] == 1
                assigned_exams = [i + 1 for i in V if x[i, j].x > 0.5]  # convert back to 1-based
                print(f"Time slot {j + 1}: Exams {assigned_exams} (proctors used: {sum(r[i - 1] for i in assigned_exams)}/{R})")
    else:
        print("No feasible solution found or an error occurred.")

# Test code 
# create a test_data.json just for testing
solve_natural_formulation('test_data.json')