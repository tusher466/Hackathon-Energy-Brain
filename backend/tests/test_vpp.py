import sys
sys.path.insert(0, "E:/Project/backend")
from app.ml.optimizer import optimize_ev_fleet
from app.ml.rl_agent import dispatch_with_rl_and_optimizer
import random

def test_soc_guarantee():
    evs = [
        {"id": "EV-1", "arrival_hour": 0, "departure_hour": 8, "initial_soc_kwh": 10, "required_soc_kwh": 40, "capacity_kwh": 50, "max_charge_kw": 7},
        {"id": "EV-2", "arrival_hour": 18, "departure_hour": 6, "initial_soc_kwh": 20, "required_soc_kwh": 45, "capacity_kwh": 60, "max_charge_kw": 7},
    ]
    batteries = []
    flexs = []
    price = [0.3]*8 + [0.1]*8 + [0.3]*8
    carbon = [0.5]*24
    result = dispatch_with_rl_and_optimizer(evs, batteries, flexs, price, carbon, 1000, 0.5, 1.0, 24)
    for ev in evs:
        sched = result["ev_schedules"][ev["id"]]
        total = sum(sched)
        needed = ev["required_soc_kwh"] - ev["initial_soc_kwh"]
        print(f"{ev['id']} needed {needed} delivered {total}")
        assert abs(total - needed) < 1e-3 or total >= needed*0.99, "SoC not guaranteed"

def test_peak_reduction():
    evs = [
        {"id": "EV-1", "arrival_hour": 0, "departure_hour": 23, "initial_soc_kwh": 10, "required_soc_kwh": 30, "capacity_kwh": 50, "max_charge_kw": 7},
    ]
    price = [0.4 if h in [18,19,20] else 0.1 for h in range(24)]
    carbon = [0.5]*24
    from app.ml.optimizer import compute_aggregates
    result = dispatch_with_rl_and_optimizer(evs, [], [], price, carbon, 10, 0.5, 2.0, 24)
    peak_before = max(result["baseline_agg"])
    peak_after = max(result["optimized_agg"])
    print(f"peak before {peak_before} after {peak_after}")
    assert peak_after <= peak_before + 1e-6, "Peak should not increase with high mu"

if __name__ == "__main__":
    test_soc_guarantee()
    test_peak_reduction()
