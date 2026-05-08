# --- START OF FILE main.py ---
import os
import pandas as pd
from solvers import solve_natural_formulation, solve_clique_formulation, solve_extended_formulation


def run_experiments_on_dataset1():
    dataset_path = "./dataset1/"
    time_limit = 120  # 120 seconds as required
    all_results = []

    # 1. find all real json files in the dataset1 folder 
    instance_files = [f for f in os.listdir(dataset_path)
                      if f.endswith('.json') and not f.startswith('._')]
    instance_files.sort()  # sort by filenames

    print(f"Found {len(instance_files)} instance files, starting...\n\n")

    # 2. Start looping through each file
    for filename in instance_files:
        filepath = os.path.join(dataset_path, filename)
        print(f"========== Processing instance: {filename} ==========")

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

        # model 2
        print("  Solving 2_Extended...")
        res_2 = solve_extended_formulation(filepath, time_limit)
        res_2['instance'] = filename
        all_results.append(res_2)

    # 3. Convert results into a dataframe and save
    print("\n========== Generating report ==========")
    df = pd.DataFrame(all_results)

    # Reorder columns
    cols = ['instance', 'formulation', 'is_optimal', 'obj_val', 'lp_relaxation', 'node_count', 'solve_time']
    df = df[cols]

    print(df.to_string())  # Print preview 

    # Export as CSV file
    df.to_csv("results_3(a).csv", index=False)
    print("\nData successfully saved to 'results_3(a).csv'！")


if __name__ == "__main__":
    run_experiments_on_dataset1()