# Backend/app.py — top of file
from flask import Flask, request, jsonify, render_template
import pandas as pd
from pathlib import Path
from datetime import datetime

# Base dir pointing to the Backend folder (where this file lives)
BASE_DIR = Path(__file__).resolve().parent

# Frontend files are in ../Frontend relative to this file
FRONTEND_DIR = BASE_DIR.parent / "Frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

# Create Flask app with explicit template/static folder locations
app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR)
)

# Data folder inside Backend
DATA_DIR = BASE_DIR / "data"
BAT_FILE = DATA_DIR / "batting_100_players.csv"
BOWL_FILE = DATA_DIR / "bowling_100_players.csv"
# (If you also keep Sample_Data as a separate folder, we'll read from DATA_DIR or Sample_Data explicitly)


# ---- In-memory stores ----
# list of dicts: {"player_name","match_date","performance_type","performance_value"}
player_data = []

# list of dicts: {"timestamp","alert_message"}
alerts = []

# ---- Helper: analysis rules (same as before) ----
def analyze_performance_row(row):
    """
    row: dict with keys:
      player_name, match_date, performance_type, performance_value
    Returns: list of alert_message strings (can be empty)
    """
    alerts_out = []
    ptype = str(row.get("performance_type", "")).lower()
    val = row.get("performance_value", "")
    player = row.get("player_name", "Unknown")

    # numeric conversion if possible
    try:
        v = float(val)
    except Exception:
        v = None

    if ptype == "batting" and v is not None and v > 150:
        alerts_out.append(f"High Strike Rate by {player} ({v})")

    if ptype == "bowling" and v is not None and v < 6:
        alerts_out.append(f"Good Bowling by {player} (Economy {v})")

    if ptype == "fielding":
        try:
            fv = float(val)
            if fv > 0:
                alerts_out.append(f"Missed Fielding Opportunity by {player} ({int(fv)} missed)")
        except Exception:
            if "miss" in str(val).lower():
                alerts_out.append(f"Missed Fielding Opportunity by {player} (reported)")

    return alerts_out

# ---- Load initial data (optional) ----
def load_initial_data():
    """
    Read batting_100_players.csv and bowling_100_players.csv (if present)
    and populate the in-memory player_data list. This does NOT write anything to disk.
    """
    # batting -> use strike_rate as performance_value
    if BAT_FILE.exists():
        try:
            bat_df = pd.read_csv(BAT_FILE)
            # expect columns: player_name, runs, balls_faced, strike_rate
            if "player_name" in bat_df.columns and "strike_rate" in bat_df.columns:
                for _, r in bat_df.iterrows():
                    player_data.append({
                        "player_name": r["player_name"],
                        "match_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "performance_type": "batting",
                        "performance_value": str(r["strike_rate"])
                    })
        except Exception:
            pass

    # bowling -> use economy as performance_value
    if BOWL_FILE.exists():
        try:
            bowl_df = pd.read_csv(BOWL_FILE)
            # expect columns: player_name, overs, wickets, economy
            if "player_name" in bowl_df.columns and "economy" in bowl_df.columns:
                for _, r in bowl_df.iterrows():
                    player_data.append({
                        "player_name": r["player_name"],
                        "match_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "performance_type": "bowling",
                        "performance_value": str(r["economy"])
                    })
        except Exception:
            pass

# ---- Add alerts to in-memory list (no console, no CSV) ----
def add_alerts_in_memory(alert_messages):
    """Append new alerts to in-memory alerts list with current timestamp."""
    if not alert_messages:
        return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for am in alert_messages:
        # avoid duplicate identical alert strings at same timestamp granularity is not necessary
        alerts.append({"timestamp": ts, "alert_message": am})

load_initial_data()
# ---- Generate alerts for players loaded from CSV files ----
def generate_alerts_for_loaded_data():
    existing_msgs = set(a["alert_message"] for a in alerts)
    new_alerts = []
    for entry in player_data:
        msgs = analyze_performance_row(entry)
        for m in msgs:
            if m not in existing_msgs:
                new_alerts.append(m)
                existing_msgs.add(m)
    add_alerts_in_memory(new_alerts)

# Run alert check for all loaded CSV players
generate_alerts_for_loaded_data()

# ---- Routes ----
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/player-data', methods=['GET'])
def get_player_data():
    # return the in-memory player_data list as JSON
    return jsonify(player_data)

@app.route('/player-data', methods=['POST'])
def post_player_data():
    """
    Accept JSON:
    {
      "player_name": "...",
      "match_date": "YYYY-MM-DD",
      "performance_type": "batting"|"bowling"|"fielding",
      "performance_value": "<value>"
    }
    Adds to memory only (no CSV write), returns any alerts generated.
    """
    data = request.get_json(force=True)
    required = ["player_name", "match_date", "performance_type", "performance_value"]
    for k in required:
        if k not in data:
            return jsonify({"error": f"Missing field {k}"}), 400

    # append to in-memory store
    entry = {
        "player_name": data["player_name"],
        "match_date": data["match_date"],
        "performance_type": data["performance_type"],
        "performance_value": str(data["performance_value"])
    }
    player_data.append(entry)

    # analyze and add any alerts to memory (no console/csv)
    alerts_generated = analyze_performance_row(entry)
    add_alerts_in_memory(alerts_generated)

    return jsonify({"message": "Data added in-memory", "alerts": alerts_generated}), 201

@app.route('/alerts', methods=['GET'])
def get_alerts():
    return jsonify(alerts)

# ---- Run ----
if __name__ == '__main__':
    app.run(debug=True)
