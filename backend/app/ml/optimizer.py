import numpy as np
from typing import List, Dict, Tuple
from scipy.optimize import linprog

def optimize_ev_fleet(
    evs: List[Dict],
    price_forecast: List[float],
    carbon_forecast: List[float],
    transformer_limit_kw: float,
    baseline_aggregate: List[float],
    lambda_co2: float = 0.5,
    mu_peak: float = 1.0,
    horizon: int = 24
):
    """
    Rolling horizon linear programming to minimize cost + lambda*CO2 + mu*peak proxied.
    Constraints: EV SoC must reach required by departure, SoC bounds, charge limits.
    We simplify to linear program: minimize weighted cost per hour.
    Returns schedules per EV: list of kW charging power per hour.
    """
    num_evs = len(evs)
    # We create variable per EV per hour: x_{ev,h} = charging power
    # Total variables = num_evs * horizon
    # Objective: sum_h (price_h + lambda*carbon_h) * total_charge_h + mu*peak approximate via auxiliary variable?
    # For simplicity, we minimize cost + carbon, and add peak penalty via high price during high baseline.

    # Adjusted price including peak penalty proxy: if baseline high, increase price
    adjusted_price = []
    for h in range(horizon):
        base = baseline_aggregate[h] if h < len(baseline_aggregate) else 0
        peak_penalty = mu_peak * max(0, base - transformer_limit_kw*0.8) / max(1, transformer_limit_kw) * 2.0
        p = price_forecast[h] if h < len(price_forecast) else price_forecast[-1]
        c = carbon_forecast[h] if h < len(carbon_forecast) else carbon_forecast[-1]
        adj = p + lambda_co2*c + peak_penalty
        adjusted_price.append(adj)

    # Build linprog: we minimize c^T x
    # Repeat adjusted_price for each EV? Actually cost depends only on total, but each EV sees same price per hour => duplication: objective coeff per ev,h = adjusted_price[h]
    c_obj = []
    for ev_idx in range(num_evs):
        for h in range(horizon):
            c_obj.append(adjusted_price[h])
    c_obj = np.array(c_obj)

    # Bounds: 0 <= x <= max_charge_kw if hour within arrival-departure else 0
    bounds = []
    for ev_idx, ev in enumerate(evs):
        arrival = ev['arrival_hour'] % horizon
        departure = ev['departure_hour'] % horizon
        max_charge = ev.get('max_charge_kw', 7.0)
        for h in range(horizon):
            # handle wrap-around: if arrival < departure: active if h in [arrival, departure)
            # if arrival > departure: active if h >= arrival or h < departure
            active = False
            if arrival <= departure:
                active = arrival <= h < departure
            else:
                active = h >= arrival or h < departure
            if active:
                bounds.append((0, max_charge))
            else:
                bounds.append((0,0))

    # Equality constraints: SoC delivery required
    # Sum_h x_h * efficiency (approx 1) = required - initial (if feasible)
    # Actually: sum charging = required - initial, clipped
    A_eq = []
    b_eq = []
    for ev_idx, ev in enumerate(evs):
        row = np.zeros(num_evs*horizon)
        energy_needed = ev['required_soc_kwh'] - ev['initial_soc_kwh']
        energy_needed = max(0, energy_needed)
        # distribute across hours
        for h in range(horizon):
            idx = ev_idx*horizon + h
            # 1 hour * power = energy (kWh) assuming charg power in kW and 1h step
            row[idx] = 1.0
        A_eq.append(row)
        b_eq.append(energy_needed)

    # Inequality: transformer limit: sum_ev x_{ev,h} + other_fixed? For simplicity we have baseline without EV? Actually we enforce total charging <= limit - (baseline - ev baseline?) Let's approximate limit on charging alone: sum_charging_h <= transformer_limit
    # Plus also consider we have baseline aggregate that already includes flexible? We'll enforce sum_charging_h <= limit * 0.7
    A_ub = []
    b_ub = []
    for h in range(horizon):
        row = np.zeros(num_evs*horizon)
        for ev_idx in range(num_evs):
            idx = ev_idx*horizon + h
            row[idx] = 1.0
        A_ub.append(row)
        # limit for EV charging alone maybe 60% of transformer
        b_ub.append(transformer_limit_kw * 0.6)

    # Solve
    try:
        result = linprog(c_obj, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq), bounds=bounds, method='highs')
        if not result.success:
            # fallback greedy: charge cheapest hours per EV
            schedules = {}
            for ev_idx, ev in enumerate(evs):
                arrival = ev['arrival_hour'] % horizon
                departure = ev['departure_hour'] % horizon
                # available hours sorted by price
                available = []
                for h in range(horizon):
                    active = False
                    if arrival <= departure:
                        active = arrival <= h < departure
                    else:
                        active = h >= arrival or h < departure
                    if active:
                        available.append((adjusted_price[h], h))
                available.sort()
                needed = ev['required_soc_kwh'] - ev['initial_soc_kwh']
                sched = [0.0]*horizon
                for price, h in available:
                    if needed <=0:
                        break
                    charge = min(ev.get('max_charge_kw',7.0), needed)
                    sched[h]=charge
                    needed-=charge
                schedules[ev['id']] = sched
            return schedules
        x = result.x
        schedules = {}
        for ev_idx, ev in enumerate(evs):
            sched = []
            for h in range(horizon):
                idx = ev_idx*horizon + h
                sched.append(float(max(0, x[idx])))
            schedules[ev['id']] = sched
        return schedules
    except Exception as e:
        # ultimate fallback
        schedules = {}
        for ev in evs:
            sched = [0.0]*horizon
            needed = max(0, ev['required_soc_kwh'] - ev['initial_soc_kwh'])
            # charge evenly
            arrival = ev['arrival_hour'] % horizon
            departure = ev['departure_hour'] % horizon
            active_hours = []
            for h in range(horizon):
                if arrival <= departure:
                    if arrival <= h < departure:
                        active_hours.append(h)
                else:
                    if h >= arrival or h < departure:
                        active_hours.append(h)
            if active_hours:
                per_hour = needed / len(active_hours)
                for h in active_hours:
                    sched[h] = min(per_hour, ev.get('max_charge_kw',7.0))
            schedules[ev['id']] = sched
        return schedules

def optimize_batteries(batteries: List[Dict], price_forecast: List[float], horizon: int):
    """Simple arbitrage: charge low price, discharge high price."""
    sorted_hours = sorted(enumerate(price_forecast), key=lambda x: x[1])
    low_hours = [h for h,_ in sorted_hours[:horizon//3]]
    high_hours = [h for h,_ in sorted_hours[-horizon//3:]]
    schedules = {}
    for bat in batteries:
        sched = [0.0]*horizon
        soc = bat['initial_soc_kwh']
        cap = bat['capacity_kwh']
        max_c = bat['max_charge_kw']
        max_d = bat['max_discharge_kw']
        # charge low
        for h in low_hours:
            if soc >= cap*0.9:
                break
            charge = min(max_c, cap-soc)
            sched[h] = charge  # positive charge
            soc += charge * bat.get('efficiency',0.92)
        # discharge high
        for h in high_hours:
            if soc <= cap*0.1:
                break
            discharge = min(max_d, soc)
            sched[h] = -discharge
            soc -= discharge
        schedules[bat['id']] = sched
    return schedules

def optimize_flexible_loads(loads: List[Dict], price_forecast: List[float], horizon: int):
    schedules = {}
    sorted_hours = sorted(enumerate(price_forecast), key=lambda x: x[1])
    for fl in loads:
        sched = [0.0]*horizon
        # flexible_hours defines allowed window
        allowed = set(fl['flexible_hours'])
        needed = fl['duration_hours']
        # pick cheapest allowed hours
        candidates = [(price, h) for h, price in enumerate(price_forecast) if h in allowed]
        candidates.sort()
        for _, h in candidates[:needed]:
            sched[h] = fl['power_kw']
        schedules[fl['id']] = sched
    return schedules

def compute_aggregates(ev_schedules, bat_schedules, flex_schedules, horizon):
    agg = [0.0]*horizon
    for sched in ev_schedules.values():
        for h in range(horizon):
            agg[h] += abs(sched[h])
    for sched in bat_schedules.values():
        for h in range(horizon):
            # net charging positive increases load, negative decreases
            agg[h] += sched[h]  # discharge reduces
    for sched in flex_schedules.values():
        for h in range(horizon):
            agg[h] += sched[h]
    return agg
