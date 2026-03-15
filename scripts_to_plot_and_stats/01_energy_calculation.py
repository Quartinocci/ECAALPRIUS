import pandas as pd
import os
import glob

#code writing assisted by AI

def calculate_energy(current_power_mw, current_time_ms, previous_time_ms):
    """
    Calculate energy used in Joules.
    
    Args:
        current_power_mw: Power in milliwatts
        current_time_ms: Current time in milliseconds
        previous_time_ms: Previous time in milliseconds
    
    Returns:
        Energy in Joules
    """
    # Convert mW to W and ms to s
    power_w = current_power_mw / 1000.0
    delta_time_s = (current_time_ms - previous_time_ms) / 1000.0
    
    # Energy in Joules: E = P * t
    energy_j = power_w * delta_time_s
    
    return energy_j

def process_csv(input_file, output_file):
    """
    Process CSV file and add energy_used_by_section column.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    # Read CSV into DataFrame
    df = pd.read_csv(input_file)
    
    # Calculate energy for each row using vectorized operations
    df['energy_used_by_section'] = calculate_energy(
        df['currentPower_mW'],
        df['current_time'],
        df['previoustime']
    )
    
    # Save to new CSV
    df.to_csv(output_file, index=False)
    
    print(f"Processing complete! Output saved to {output_file}")
    print(f"Processed {len(df)} rows")

if __name__ == "__main__":
    # Find the first CSV file in the current directory
    csv_files = glob.glob("*.csv")
    
    # Filter out any previously generated files
    csv_files = [f for f in csv_files if not ('_energy_section' in f or '_master_energy' in f)]
    
    if not csv_files:
        print("Error: No CSV file found in the current directory")
        exit(1)
    
    input_csv = csv_files[0]
    
    # Create output filename by adding _energy_section before .csv extension
    base_name = os.path.splitext(input_csv)[0]
    output_csv = f"{base_name}_energy_section.csv"
    
    print(f"Processing: {input_csv}")
    process_csv(input_csv, output_csv)
