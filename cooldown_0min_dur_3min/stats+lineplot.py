import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
import glob
import os

# Code written with assistance of AI
csv_files = glob.glob("*master_energy_to_merge.csv")

# Check if there's more than one matching file
if len(csv_files) > 1:
    raise ValueError(f"Multiple files found: {csv_files}. Please ensure there's only one matching file.")
elif len(csv_files) == 0:
    raise FileNotFoundError("No matching CSV file found.")
    
csv_file = csv_files[0]
    
filename_original = os.path.splitext(os.path.basename(csv_file))[0].replace("master_energy_to_merge", "").rstrip("_")
print("found file "+str(filename_original))

# Read the first matching file
df = pd.read_csv(csv_file)

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
plt.xlabel('Consecutive run order', fontsize=20)
plt.ylabel('Energy (J)', fontsize=20)
#plt.title('Energy used over consecutive runs', fontsize=20)


plt.xticks(fontsize=16)   # X axis values
plt.yticks(fontsize=16)   # Y axis values

plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save the plot
plt.savefig(filename_original+".png", dpi=300, bbox_inches='tight')
print("Plot saved as: "+filename_original+".png")

# Optionally still show it
#plt.show()
