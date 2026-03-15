import subprocess
import json
from pathlib import Path

base_path = Path(__file__).parent
scripts_folder = base_path / "scripts_to_plot_and_stats"
results_folder = base_path / "results"
config_file = base_path / "pipeline_config.json"

# Load pipeline configuration
with open(config_file, 'r') as f:
    config = json.load(f)

# Get experiment folders
experiment_folders = sorted([
    f for f in base_path.iterdir()
    if f.is_dir() and f.name not in ["folder_python_scripts", "results"]
])

# Build dictionary: {order: (script_name, location)}
scripts_dict = {}
for location, scripts in config.items():
    for script_name, order in scripts.items():
        scripts_dict[order] = (script_name, location)

print(f"Found {len(experiment_folders)} experiment folders")
print(f"Loaded {len(scripts_dict)} scripts from pipeline configuration\n")


def print_status(result, indent=""):
    """Print the status and output of a subprocess result."""
    if result.stdout:
        print(f"{indent}{result.stdout}")
    
    if result.returncode != 0:
        print(f"{indent}❌ Error:")
        print(f"{indent}{result.stderr}")
    else:
        print(f"{indent}✅ Success")


def run_single_location(script_path, work_dir, location_name):
    """Run a script in a single directory location."""
    if not work_dir.exists():
        print(f"⚠️  {location_name.capitalize()} folder not found, skipping")
        return
    
    result = subprocess.run(
        ["python", str(script_path)],
        cwd=work_dir,
        capture_output=True,
        text=True
    )
    
    print_status(result)


def run_in_multiple_folders(script_path, folders):
    """Run a script in multiple experiment folders."""
    for folder in folders:
        print(f"  Processing folder: {folder.name}")
        
        result = subprocess.run(
            ["python", str(script_path)],
            cwd=folder,
            capture_output=True,
            text=True
        )
        
        print_status(result, indent="    ")


# Execute scripts in order
for order in sorted(scripts_dict.keys()):
    script_name, location = scripts_dict[order]
    script_path = scripts_folder / script_name
    
    print(f"{'='*60}")
    print(f"Step {order}: {script_name} (location: {location})")
    print(f"{'='*60}")
    
    if location == "experiments":
        run_in_multiple_folders(script_path, experiment_folders)
    
    elif location == "main":
        run_single_location(script_path, base_path, "main")
    
    elif location == "results":
        run_single_location(script_path, results_folder, "results")
    
    print()

print("="*60)
print("Pipeline completed!")
