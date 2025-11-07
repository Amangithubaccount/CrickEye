# load_data.py
import pandas as pd
from pathlib import Path

# Define file paths
DATA_DIR = Path("data")
bat_file = DATA_DIR / "batting_100_players.csv"
bowl_file = DATA_DIR / "bowling_100_players.csv"
out_file = DATA_DIR / "player_performance.csv"

# Check if files exist
if not bat_file.exists():
    raise FileNotFoundError(f"{bat_file} not found")
if not bowl_file.exists():
    raise FileNotFoundError(f"{bowl_file} not found")

# Read the batting and bowling CSVs
bat = pd.read_csv(bat_file)
bowl = pd.read_csv(bowl_file)

# Prepare batting data (use strike_rate as performance_value)
bat_rows = pd.DataFrame({
    "player_name": bat["player_name"],
    "match_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
    "performance_type": "batting",
    "performance_value": bat["strike_rate"].astype(str)
})

# Prepare bowling data (use economy as performance_value)
bowl_rows = pd.DataFrame({
    "player_name": bowl["player_name"],
    "match_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
    "performance_type": "bowling",
    "performance_value": bowl["economy"].astype(str)
})

# Combine and save
combined = pd.concat([bat_rows, bowl_rows], ignore_index=True)
combined.to_csv(out_file, index=False)
print(f"✅ Wrote {out_file} with {len(combined)} rows")
