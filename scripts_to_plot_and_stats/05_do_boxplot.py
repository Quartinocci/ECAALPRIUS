import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

#code writing assisted by AI

# Define the path to the CSV file (in the same directory as the script)
csv_path = 'all_protocols_master_energy.csv'

# Check if file exists
if not os.path.exists(csv_path):
    print(f"ERROR: File not found at {csv_path}")
    print("Please make sure 'master_measurements.csv' is in the same directory as this script")
    exit()

# Read and clean the CSV file
df = pd.read_csv(csv_path, sep=',', skipinitialspace=True)
df.columns = df.columns.str.strip()
df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

print("Column names found:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
print("\n")

# Check if the required columns exist
required_cols = ['current_benchmark', 'protocol', 'total_energy_J']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    print(f"ERROR: Missing columns: {missing_cols}")
    print("Please check your CSV file column names.")
    exit()

# Set style
sns.set_style("whitegrid")

# Get unique benchmarks
benchmarks = sorted(df['current_benchmark'].unique())

def detect_gap(benchmark_data, gap_threshold=30):
    """Detect if there's a large gap between protocol ranges."""
    protocol_ranges = []
    for protocol in benchmark_data['protocol'].unique():
        proto_data = benchmark_data[benchmark_data['protocol'] == protocol]['total_energy_J']
        protocol_ranges.append((proto_data.min(), proto_data.max()))
    
    protocol_ranges.sort()
    
    if len(protocol_ranges) > 1:
        for i in range(len(protocol_ranges) - 1):
            gap = protocol_ranges[i+1][0] - protocol_ranges[i][1]
            if gap >= gap_threshold:
                break_start = protocol_ranges[i][1] + 5
                break_end = protocol_ranges[i+1][0] - 5
                return True, break_start, break_end
    
    return False, 0, 0

def add_break_marks(ax1, ax2):
    """Add diagonal break marks between split axes."""
    d = 0.015
    kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False, linewidth=1)
    ax1.plot((-d, +d), (-d, +d), **kwargs)
    ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    
    kwargs.update(transform=ax2.transAxes)
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

def create_broken_axis_plot(benchmark_data, benchmark, break_start, break_end):
    """Create a box plot with broken y-axis."""
    max_val = benchmark_data['total_energy_J'].max()
    min_val = benchmark_data['total_energy_J'].min()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), sharex=True, 
                                    gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.05})
    
    # Plot on both axes
    sns.boxplot(data=benchmark_data, x='protocol', y='total_energy_J', palette='Set2', ax=ax1)
    sns.boxplot(data=benchmark_data, x='protocol', y='total_energy_J', palette='Set2', ax=ax2)
    
    # Set the y-axis limits for the break
    ax1.set_ylim(break_end, max_val + 5)
    ax2.set_ylim(min_val - 5, break_start)
    
    # Style the split
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.xaxis.tick_top()
    ax1.tick_params(labeltop=False)
    ax2.xaxis.tick_bottom()
    
    add_break_marks(ax1, ax2)
    
    # Labels
    ax1.set_xlabel('')
    ax2.set_xlabel('Protocol', fontsize=10)
    ax2.set_ylabel('Energy Used by Run', fontsize=10)
    ax1.set_ylabel('')
    fig.text(0.04, 0.5, 'Energy Used by Run', va='center', rotation='vertical', fontsize=10)
    fig.suptitle(f'Energy Usage Distribution - Benchmark {benchmark}', 
                 fontsize=12, fontweight='bold', y=0.995)
    
    # Grid
    ax1.grid(axis='y', alpha=0.3)
    ax2.grid(axis='y', alpha=0.3)
    
    return fig

def create_normal_plot(benchmark_data, benchmark):
    """Create a normal box plot."""
    plt.figure(figsize=(8, 9))
    sns.boxplot(data=benchmark_data, x='protocol', y='total_energy_J', palette='Set2')

    if benchmark == 1:
        benchmark_label = "Light"
    elif benchmark == 2:
        benchmark_label = "Heavy"
    else:
        benchmark_label = benchmark
    
    #plt.title(f'Energy Usage Distribution - {benchmark_label} Benchmark', fontsize=20)
    plt.xlabel('Protocol', fontsize=20)
    plt.ylabel('Energy (J)', fontsize=20)
    
    plt.xticks(rotation=35, ha='right', fontsize=16)
    plt.yticks(fontsize=16)
    
    plt.grid(axis='y', alpha=0.3)

# Generate a box plot for each benchmark
for benchmark in benchmarks:
    benchmark_data = df[df['current_benchmark'] == benchmark]
    
    use_broken_axis, break_start, break_end = detect_gap(benchmark_data)
    
    if use_broken_axis:
        create_broken_axis_plot(benchmark_data, benchmark, break_start, break_end)
    else:
        create_normal_plot(benchmark_data, benchmark)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(f'boxplot_benchmark{benchmark}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f'Generated: boxplot_benchmark{benchmark}.png')

print('\nAll box plots generated successfully!')
