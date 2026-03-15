import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

#code writing assisted by AI

# Load your data
df = pd.read_csv('cooldown_test_2/cooldown_test_2_master_energy_to_merge.csv')

#-----------------------------------------------------------------------------------
# Check that we have only one type of benchmark
unique_benchmarks = df['current_benchmark'].nunique()
if unique_benchmarks > 1:
    print("⚠️ Looks like you got more than one type of benchmark in this CSV, are you sure is the CSV about cooldowns?")
    print(f"Found {unique_benchmarks} different benchmarks: {df['current_benchmark'].unique()}")
else:
    print(f"✓ All rows have the same benchmark: {df['current_benchmark'].iloc[0]}")

print()

# Print standard deviation of total_energy_J
energy_std = df['total_energy_J'].std()
print(f"Standard Deviation of total_energy_J: {energy_std:.4f}")
print()

#-----------------------------------------------------------------------------------

# Spearman correlation between current_runs order and total_energy_J
correlation, p_value = spearmanr(df['current_runs'], df['total_energy_J'])

print(f"Spearman's rho: {correlation:.4f}")
print(f"P-value: {p_value:.4f}")

# Interpretation
if p_value < 0.05:
    if correlation > 0:
        print(f"⚠️ Significant POSITIVE trend (total_energy_J increases over runs)")
    else:
        print(f"⚠️ Significant NEGATIVE trend (total_energy_J decreases over runs)")
else:
    print(f"✓ No significant trend (likely no carryover effect)")

# Visualize
plt.figure(figsize=(8, 5))
plt.plot(df['current_runs'], df['total_energy_J'], 'o-')
plt.xlabel('current_runs Order')
plt.ylabel('total_energy_J')
plt.title('total_energy_J vs current_runs Order')
plt.grid(True, alpha=0.3)
#plt.show()

#----------------------------------------------------------------------------------

# Create line plot
plt.figure(figsize=(10, 6))
plt.plot(df['current_runs'], df['total_energy_J'], 'o-', linewidth=2, markersize=8)
plt.xlabel('current_runs Order', fontsize=12)
plt.ylabel('total_energy_J', fontsize=12)
plt.title('total_energy_J vs current_runs Order', fontsize=14)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save the plot
plt.savefig('energy_vs_run_order.png', dpi=300, bbox_inches='tight')
print("Plot saved as 'energy_vs_run_order.png'")

# Optionally still show it
#plt.show()
