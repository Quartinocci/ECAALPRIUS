import pandas as pd
import numpy as np
from scipy import stats

#code writing assisted by AI

# Load the data
csv_path = 'all_protocols_master_energy.csv'
df = pd.read_csv(csv_path, sep=',', skipinitialspace=True)

print("=== Data Overview ===")
print(df.head())
print(f"\nShape: {df.shape}")
print(f"\nBenchmarks: {df['current_benchmark'].unique()}")
print(f"Protocols: {df['protocol'].unique()}")
print(f"Runs per protocol per benchmark: {df.groupby(['current_benchmark', 'protocol']).size()}")

# Analyze each benchmark separately
benchmarks = df['current_benchmark'].unique()

results = []

for benchmark in benchmarks:
    print(f"\n{'='*60}")
    print(f"BENCHMARK: {benchmark}")
    print('='*60)
    
    # Filter data for this benchmark
    benchmark_data = df[df['current_benchmark'] == benchmark]
    
    # Get protocols for this benchmark
    protocols = benchmark_data['protocol'].unique()
    
    # Prepare data for Kruskal-Wallis test
    # Create groups: one list of energy values per protocol
    groups = [benchmark_data[benchmark_data['protocol'] == p]['total_energy_J'].values 
              for p in protocols]
    
    # Perform Kruskal-Wallis test
    h_stat, p_value = stats.kruskal(*groups)
    
    # Calculate descriptive statistics
    stats_df = benchmark_data.groupby('protocol')['total_energy_J'].agg([
        ('median', 'median'),
        ('mean', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max'),
        ('count', 'count')
    ]).round(3)
    
    print("\nDescriptive Statistics:")
    print(stats_df)
    
    # Calculate range across protocols
    overall_min = benchmark_data['total_energy_J'].min()
    overall_max = benchmark_data['total_energy_J'].max()
    energy_range = overall_max - overall_min
    median_energy = benchmark_data['total_energy_J'].median()
    range_percentage = (energy_range / median_energy) * 100
    
    print(f"\nEnergy Range: {energy_range:.3f} J ({range_percentage:.2f}% of median)")
    print(f"Overall Median: {median_energy:.3f} J")
    
    # Kruskal-Wallis results
    print(f"\n--- Kruskal-Wallis Test ---")
    print(f"H-statistic: {h_stat:.4f}")
    print(f"p-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("✓ Statistically significant differences detected (p < 0.05)")
        
        # Calculate effect size (epsilon-squared for Kruskal-Wallis)
        n = len(benchmark_data)
        k = len(protocols)
        epsilon_squared = (h_stat - k + 1) / (n - k)
        print(f"Effect size (ε²): {epsilon_squared:.4f}")
        
        # Interpret effect size
        if epsilon_squared < 0.01:
            effect_interpretation = "negligible"
        elif epsilon_squared < 0.06:
            effect_interpretation = "small"
        elif epsilon_squared < 0.14:
            effect_interpretation = "medium"
        else:
            effect_interpretation = "large"
        print(f"Effect size interpretation: {effect_interpretation}")
        
        # Post-hoc pairwise comparisons (Dunn's test alternative using Mann-Whitney U)
        print("\n--- Pairwise Comparisons (Mann-Whitney U with Bonferroni correction) ---")
        from itertools import combinations
        n_comparisons = len(list(combinations(protocols, 2)))
        alpha_corrected = 0.05 / n_comparisons
        
        for p1, p2 in combinations(protocols, 2):
            group1 = benchmark_data[benchmark_data['protocol'] == p1]['total_energy_J'].values
            group2 = benchmark_data[benchmark_data['protocol'] == p2]['total_energy_J'].values
            u_stat, p_val = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            
            median_diff = np.median(group1) - np.median(group2)
            sig_marker = "***" if p_val < alpha_corrected else ""
            print(f"{p1} vs {p2}: p={p_val:.4f} {sig_marker}, median diff={median_diff:.3f} J")
        
        print(f"\n(*** indicates significance after Bonferroni correction: α={alpha_corrected:.4f})")
        
    else:
        print("✗ No statistically significant differences detected (p ≥ 0.05)")
    
    # Store results
    results.append({
        'benchmark': benchmark,
        'h_statistic': h_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'energy_range_J': energy_range,
        'range_percentage': range_percentage,
        'median_energy_J': median_energy
    })

# Summary table
print("\n" + "="*60)
print("SUMMARY OF ALL BENCHMARKS")
print("="*60)
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# Save results to CSV
results_df.to_csv('kruskal_wallis_results.csv', index=False)
print("\nResults saved to: kruskal_wallis_results.csv")
