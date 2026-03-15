import pandas as pd
import sys
from itertools import combinations

#code writing assisted by AI

# Check if threshold is provided via command line
if len(sys.argv) > 1:
    try:
        threshold_MAD_SD = float(sys.argv[1])
        print(f"Using MAD-based SD threshold (MAD × 1.4826): {threshold_MAD_SD} J")
    except ValueError:
        print("Error: Invalid threshold value. Please provide a number.")
        sys.exit(1)
else:
    threshold_input = input(
        "Enter the MAD-based SD value (MAD × 1.4826, in J) [press Enter to skip]: "
    )
    if threshold_input.strip() == "":
        print("No threshold provided. Skipping practical significance check.")
        threshold_MAD_SD = None
    else:
        try:
            threshold_MAD_SD = float(threshold_input)
        except ValueError:
            print("Error: Invalid threshold value. Please provide a number.")
            sys.exit(1)

# Load the data
csv_path = 'all_protocols_master_energy.csv'
df = pd.read_csv(csv_path, sep=',', skipinitialspace=True)

print("\n=== Data Overview ===")
print(f"Shape: {df.shape}")
print(f"Benchmarks: {df['current_benchmark'].unique()}")
print(f"Protocols: {df['protocol'].unique()}")

# Calculate MEDIAN for each benchmark-protocol combination
medians = (
    df.groupby(['current_benchmark', 'protocol'])['total_energy_J']
      .median()
      .reset_index()
)
medians.columns = ['current_benchmark', 'protocol', 'median_energy_J']

print("\n" + "="*80)
print("MEDIAN ENERGY FOR EACH BENCHMARK-PROTOCOL COMBINATION")
print("="*80)
print(medians.to_string(index=False))

# If no threshold provided, exit here
if threshold_MAD_SD is None:
    print("\nScript completed (no practical significance analysis performed).")
    sys.exit(0)

# Get unique benchmarks
benchmarks = df['current_benchmark'].unique()

print("\n" + "="*80)
print(f"PAIRWISE COMPARISONS (MAD-based SD Threshold: {threshold_MAD_SD} J)")
print("="*80)

# For each benchmark, calculate pairwise differences
all_results = []

for benchmark in benchmarks:
    print(f"\n--- BENCHMARK: {benchmark} ---")

    # Filter medians for this benchmark
    benchmark_medians = medians[medians['current_benchmark'] == benchmark]

    # Get protocols for this benchmark
    protocols = benchmark_medians['protocol'].values

    # Create a dictionary for easy lookup
    median_dict = dict(
        zip(benchmark_medians['protocol'], benchmark_medians['median_energy_J'])
    )

    # Calculate all pairwise differences
    benchmark_results = []
    for p1, p2 in combinations(protocols, 2):
        diff = median_dict[p1] - median_dict[p2]
        abs_diff = abs(diff)
        is_significant = abs_diff > threshold_MAD_SD

        benchmark_results.append({
            'Protocol 1': p1,
            'Protocol 2': p2,
            'Abs Diff (J)': round(abs_diff, 3),
            'Practically Sig?': 'YES' if is_significant else 'NO'
        })

        all_results.append({
            'Benchmark': benchmark,
            'Protocol 1': p1,
            'Protocol 2': p2,
            'Abs Diff (J)': round(abs_diff, 3),
            'Threshold (J)': threshold_MAD_SD,
            'Practically Sig?': 'YES' if is_significant else 'NO'
        })

    # Print as table for this benchmark
    results_df = pd.DataFrame(benchmark_results)
    print(results_df.to_string(index=False))

# Print overall summary
print("\n" + "="*80)
print("COMPLETE SUMMARY - ALL BENCHMARKS")
print("="*80)
summary_df = pd.DataFrame(all_results)
print(summary_df.to_string(index=False))

# Save to CSV
summary_df.to_csv('pairwise_differences_summary.csv', index=False)
print("\n✓ Results saved to: pairwise_differences_summary.csv")
