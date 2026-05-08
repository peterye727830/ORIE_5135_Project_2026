# --- START OF FILE main_3b.py ---
import os
import pandas as pd
# only need 1a and 1b
from solvers import solve_natural_formulation, solve_clique_formulation


def run_experiments_on_dataset2():
    dataset_path = "./dataset2/"
    time_limit = 600  # 600 seconds as required
    all_results = []

    #  find all json files in dataset2 
    instance_files = [f for f in os.listdir(dataset_path)
                      if f.endswith('.json') and not f.startswith('._')]
    instance_files.sort()

    print(f"Found {len(instance_files)} Dataset 2 instance files, starting (600s limit)...\n")

    for filename in instance_files:
        filepath = os.path.join(dataset_path, filename)
        print(f"========== Processing large instance: {filename} ==========")

        # model 1a
        print("  Solving 1a_Natural...")
        res_1a = solve_natural_formulation(filepath, time_limit)
        res_1a['instance'] = filename
        all_results.append(res_1a)

        # model 1b
        print("  Solving 1b_Clique...")
        res_1b = solve_clique_formulation(filepath, time_limit)
        res_1b['instance'] = filename
        all_results.append(res_1b)

        # Model 2a is intentionally skipped here

    # Generate and save
    print("\n========== generating report ==========")
    df = pd.DataFrame(all_results)

    cols = ['instance', 'formulation', 'is_optimal', 'obj_val', 'lp_relaxation', 'node_count', 'solve_time']
    df = df[cols]

    print(df.to_string())

    df.to_csv("results_3(b).csv", index=False)
    print("\nLarge-scale data successfully saved to 'results_3(b).csv'！")


if __name__ == "__main__":
    run_experiments_on_dataset2()