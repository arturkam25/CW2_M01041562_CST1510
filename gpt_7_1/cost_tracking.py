import json
from datetime import datetime, timedelta
from pathlib import Path

# Ścieżki
DB_PATH = Path("db")
COSTS_PATH = DB_PATH / "costs.json"

def log_daily_cost(cost_usd):
    today = datetime.now().strftime("%Y-%m-%d")

    if not DB_PATH.exists():
        DB_PATH.mkdir()
    if not COSTS_PATH.exists():
        with open(COSTS_PATH, "w") as f:
            json.dump({}, f)

    with open(COSTS_PATH, "r") as f:
        cost_data = json.load(f)

    if today in cost_data:
        cost_data[today] += cost_usd
    else:
        cost_data[today] = cost_usd

    with open(COSTS_PATH, "w") as f:
        json.dump(cost_data, f)

def get_cost_summary(days=60):
    if not COSTS_PATH.exists():
        return {}

    with open(COSTS_PATH, "r") as f:
        cost_data = json.load(f)

    cutoff_date = datetime.now() - timedelta(days=days)
    summary = {
        day: round(cost, 4)
        for day, cost in cost_data.items()
        if datetime.strptime(day, "%Y-%m-%d") >= cutoff_date
    }

    return dict(sorted(summary.items(), reverse=True))

def get_total_cost():
    if not COSTS_PATH.exists():
        return 0.0
    with open(COSTS_PATH, "r") as f:
        cost_data = json.load(f)
    return round(sum(cost_data.values()), 4)

def reset_costs():
    if COSTS_PATH.exists():
        with open(COSTS_PATH, "w") as f:
            json.dump({}, f)

