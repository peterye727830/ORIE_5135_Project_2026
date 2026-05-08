import json
import gurobipy as gp
from gurobipy import GRB


def solve_extended_formulation(json_file_path):
    # 1. Read data
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    m, n, R = data['m'], data['n'], data['R']
    r, edges = data['r'], data['edges']

    # Exam indices 0 to m-1
    V = list(range(m))

    # Build adjacency list for fast conflict checking
    # adj[i] is a set containing all exam indices that conflict with exam i
    adj = {i: set() for i in V}
    for u, v in edges:
        u_idx, v_idx = u - 1, v - 1
        adj[u_idx].add(v_idx)
        adj[v_idx].add(u_idx)

    # ---------------------------------------------------------
    # 2. Core algorithm: enumerate all feasible groupings
    # ---------------------------------------------------------
    feasible_groupings = []

    def dfs(start_idx, current_group, current_req):
        # As long as the group is non-empty, it's a valid candidate — save it
        if current_group:
            feasible_groupings.append(list(current_group))

        # Try adding subsequent exams
        for i in range(start_idx, m):
            # Pruning 1: if adding exam i exceeds the proctor budget, skip
            if current_req + r[i] > R:
                continue

            # Pruning 2: if exam i conflicts with any exam already in the group, skip
            conflict = False
            for j in current_group:
                if j in adj[i]:
                    conflict = True
                    break

            # If neither over budget nor conflicting, add i and continue searching
            if not conflict:
                current_group.append(i)
                dfs(i + 1, current_group, current_req + r[i])
                current_group.pop()  # Backtrack: remove i and try the next option

    # Start search from exam 0, with an empty group and zero proctor requirement
    print("Enumerating all feasible groupings (this may take a moment for large instances)...")
    dfs(0, [], 0)
    print(f"Enumeration complete! Found {len(feasible_groupings)} feasible groupings.")

    # ---------------------------------------------------------
    # 3. Create Gurobi extended model
    # ---------------------------------------------------------
    model = gp.Model("Exam_Scheduling_Extended")
    # model.setParam('OutputFlag', 0)  # Optional: suppress solver output

    # Variable: lambda_S = 1 means the k-th grouping is selected
    # The number of variables equals the number of feasible groupings
    lam = model.addVars(len(feasible_groupings), vtype=GRB.BINARY, name="lam")

    # Objective: minimize the number of selected groupings
    model.setObjective(gp.quicksum(lam[k] for k in range(len(feasible_groupings))), GRB.MINIMIZE)

    # Constraint: each exam must belong to exactly one selected grouping (Set Partitioning: == 1)
    for i in V:
        model.addConstr(
            gp.quicksum(lam[k] for k, S in enumerate(feasible_groupings) if i in S) == 1,
            name=f"Cover_{i}"
        )

    # 4. Solve
    model.setParam('TimeLimit', 120)
    model.optimize()

    # 5. Print results
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        print(f"\n--- 2(a) Extended Formulation Results ---")
        print(f"Optimal objective: {model.ObjVal}")
        print(f"B&B nodes explored: {model.NodeCount}")
        print(f"Solve time: {model.Runtime:.2f} seconds")

        # Print the selected groupings
        count = 1
        for k in range(len(feasible_groupings)):
            if lam[k].x > 0.5:  # If this grouping was selected
                assigned_exams = [i + 1 for i in feasible_groupings[k]]  # Convert to 1-based for display
                total_r = sum(r[i] for i in feasible_groupings[k])
                print(f"Selected grouping {count}: Exams {assigned_exams} (proctors used: {total_r}/{R})")
                count += 1
    else:
        print("No feasible solution found.")



# --- Test code ---
solve_extended_formulation('test_data.json')