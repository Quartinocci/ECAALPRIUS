from pathlib import Path
import pandas as pd

#code writing assisted by AI

def convert_csvs_to_parquet(root_path: Path):
    for csv_path in root_path.rglob("*.csv"):
        parquet_path = csv_path.with_suffix(".parquet")

        try:
            df = pd.read_csv(csv_path)
            df.to_parquet(parquet_path, engine="pyarrow", index=False)
            print(f"Converted: {csv_path}")
        except Exception as e:
            print(f"Failed to convert {csv_path}: {e}")

if __name__ == "__main__":
    base_path = Path(__file__).parent
    convert_csvs_to_parquet(base_path)
