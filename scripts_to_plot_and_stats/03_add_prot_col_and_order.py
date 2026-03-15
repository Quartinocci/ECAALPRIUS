import pandas as pd
import glob
import os

#code writing assisted by AI

# Find all CSV files ending with "_master_energy.csv"
csv_files = glob.glob("*_master_energy.csv")

if not csv_files:
    print("No CSV files ending with '_master_energy.csv' found in the current directory.")
else:
    for csv_file in csv_files:
        print(f"Processing: {csv_file}")
        
        # Extract the protocol name (everything before "_master_energy.csv")
        protocol_name = csv_file.replace("_master_energy.csv", "")
        
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Insert the "protocol" column as the first column
        df.insert(0, "protocol", protocol_name)
        
        # Sort the dataframe: first by "current_benchmark", then by "current_runs"
        df = df.sort_values(by=["current_benchmark", "current_runs"])
        
        # Create the output filename
        output_file = f"{protocol_name}_master_energy_to_merge.csv"
        
        # Save the modified CSV
        df.to_csv(output_file, index=False)
        
        print(f"Saved: {output_file}")
    
    print(f"\nProcessed {len(csv_files)} file(s) successfully.")
