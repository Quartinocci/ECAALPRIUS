import pandas as pd
import glob

#code writing assisted by AI

def aggregate_energy(input_file, output_file):
    """
    Aggregate energy_used_by_section by current_runs and current_benchmark.
    
    Args:
        input_file: Path to input CSV file (with energy_used_by_section column)
        output_file: Path to output CSV file
    """
    # Read CSV into DataFrame
    df = pd.read_csv(input_file)
    
    # Group by current_runs and current_benchmark, then sum energy_used_by_section
    aggregated = df.groupby(['current_runs', 'current_benchmark'])['energy_used_by_section'].sum().reset_index()
    
    # Rename the column for clarity
    aggregated.rename(columns={'energy_used_by_section': 'total_energy_J'}, inplace=True)

    # Round total_energy_J to 3 decimal places
    aggregated['total_energy_J'] = aggregated['total_energy_J'].round(4)
    
    # Save to new CSV
    aggregated.to_csv(output_file, index=False)
    
    print(f"Aggregation complete! Output saved to {output_file}")
    print(f"Total unique combinations: {len(aggregated)}")
    print(f"\nSummary statistics:")
    print(f"Mean energy per group: {aggregated['total_energy_J'].mean():.4f} J")
    print(f"Total energy across all groups: {aggregated['total_energy_J'].sum():.4f} J")

if __name__ == "__main__":
    # Find the first CSV file with _energy_section in the current directory
    csv_files = glob.glob("*_energy_section.csv")
    
    if not csv_files:
        print("Error: No CSV file with '_energy_section' found in the current directory")
        exit(1)
    
    input_csv = csv_files[0]
    
    # Create output filename by replacing _energy_section with _master_energy
    base_name = input_csv.replace('_energy_section.csv', '')
    output_csv = f"{base_name}_master_energy.csv"
    
    print(f"Processing: {input_csv}")
    aggregate_energy(input_csv, output_csv)
