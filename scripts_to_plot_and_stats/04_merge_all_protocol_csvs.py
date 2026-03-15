import pandas as pd
import os
import glob

#code writing assisted by AI

# Find all CSV files ending with "master_energy_to_merge.csv" in all subdirectories
csv_files = glob.glob("**/*master_energy_to_merge.csv", recursive=True)

if not csv_files:
    print("No CSV files ending with 'master_energy_to_merge.csv' found in subdirectories.")
else:
    print(f"Found {len(csv_files)} file(s) to merge:")
    for file in csv_files:
        print(f"  - {file}")
    
    # Read and merge all CSV files
    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        dfs.append(df)
        print(f"Loaded: {csv_file}")
    
    # Concatenate all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)

    merged_df = merged_df.sort_values(by=["protocol","current_benchmark", "current_runs"])
    
    print(f"\nMerged dataframe has {len(merged_df)} rows and {len(merged_df.columns)} columns.")
    
    # Create the results folder if it doesn't exist
    results_folder = "results"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    print(f"Results folder ready: {results_folder}")
    
    # Save the merged CSV
    output_file = os.path.join(results_folder, "all_protocols_master_energy.csv")
    merged_df.to_csv(output_file, index=False)
    
    print(f"\nSuccessfully saved merged file: {output_file}")
