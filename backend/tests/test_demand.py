import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.data.synthetic import generate_demand_timeseries
from app.ml.demand_transformer import demand_forecaster
from datetime import datetime, timedelta, timezone
import numpy as np

def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def test_demand_monotonic():
    fc = generate_demand_timeseries("BD", 3, 24)
    for p in fc:
        assert p["p10"] <= p["p50"] <= p["p90"]
    print("demand monotonic ok")

def test_demand_forecaster_training():
    hist = generate_demand_timeseries("BD", 3, 168)
    ts = [_utcnow() - timedelta(hours=168-i) for i in range(168)]
    loads = [h["p50"] for h in hist]
    temps = [25]*168
    forecasts, imp, mape, pinball = demand_forecaster.forecast(ts, loads, temps, 24)
    assert len(forecasts)==24
    for f in forecasts:
        assert f["p10"] <= f["p50"] <= f["p90"]
    print(f"mape {mape} pinball {pinball} feat {imp}")

if __name__ == "__main__":
    test_demand_monotonic()
    test_demand_forecaster_training()
