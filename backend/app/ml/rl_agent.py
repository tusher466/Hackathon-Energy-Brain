import numpy as np
from typing import List, Dict
from .optimizer import optimize_ev_fleet, optimize_batteries, optimize_flexible_loads, compute_aggregates

class FleetEnv:
    def __init__(self, evs, price_forecast, carbon_forecast, transformer_limit):
        self.evs = evs
        self.price = price_forecast
        self.carbon = carbon_forecast
        self.limit = transformer_limit
        self.horizon = len(price_forecast)

    def step_baseline(self):
        """Immediate charging baseline"""
        schedules = {}
        for ev in self.evs:
            sched = [0.0]*self.horizon
            need = max(0, ev['required_soc_kwh'] - ev['initial_soc_kwh'])
            arrival = ev['arrival_hour'] % self.horizon
            # charge immediately from arrival
            h = arrival
            while need > 0 and h < arrival+self.horizon:
                hh = h % self.horizon
                charge = min(ev.get('max_charge_kw',7.0), need)
                sched[hh] = charge
                need -= charge
                h+=1
                # stop if beyond departure
                dep = ev['departure_hour'] % self.horizon
                # simple break if we looped to departure
                if arrival <= dep:
                    if hh >= dep:
                        break
                else:
                    if arrival <= hh < 24 and hh >= dep and hh < arrival:
                        pass
            schedules[ev['id']] = sched
        return schedules

class QLearningAgent:
    """
    Very lightweight tabular Q-learning for demonstration.
    State: hour, price_bucket, aggregate load bucket.
    Action: charge level 0, 0.5*max, max per EV? Simplified to fleet-level decision.
    We'll actually learn a price threshold policy.
    """
    def __init__(self, horizon=24):
        self.horizon = horizon
        self.q_table = np.zeros((horizon, 5, 3))  # hour, price bucket, action
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2

    def price_to_bucket(self, price, price_forecast):
        # bucketize price into 5 levels
        sorted_p = sorted(price_forecast)
        # quintiles
        if price <= sorted_p[len(sorted_p)//5]:
            return 0
        elif price <= sorted_p[2*len(sorted_p)//5]:
            return 1
        elif price <= sorted_p[3*len(sorted_p)//5]:
            return 2
        elif price <= sorted_p[4*len(sorted_p)//5]:
            return 3
        else:
            return 4

    def train(self, env: FleetEnv, episodes=200):
        price_forecast = env.price
        np.random.seed(0)
        for ep in range(episodes):
            total_cost = 0
            # simulate one day
            for h in range(self.horizon):
                bucket = self.price_to_bucket(price_forecast[h], price_forecast)
                # epsilon greedy
                if np.random.rand() < self.epsilon:
                    action = np.random.randint(0,3)
                else:
                    action = int(np.argmax(self.q_table[h, bucket]))
                # action mapping: 0 = no charging, 1 = medium, 2 = high
                # reward = -price*(action level) + bonus if meeting constraints? Simplified
                reward = -price_forecast[h] * (action) + (1 if action==0 and price_forecast[h] > np.mean(price_forecast) else 0)
                # update Q
                next_h = (h+1) % self.horizon
                next_bucket = self.price_to_bucket(price_forecast[next_h], price_forecast) if next_h < self.horizon else bucket
                best_next = np.max(self.q_table[next_h, next_bucket]) if next_h < self.horizon else 0
                self.q_table[h, bucket, action] += self.alpha * (reward + self.gamma*best_next - self.q_table[h, bucket, action])

    def get_policy(self, price_forecast):
        policy = []
        for h in range(len(price_forecast)):
            bucket = self.price_to_bucket(price_forecast[h], price_forecast)
            action = int(np.argmax(self.q_table[h, bucket]))
            policy.append(action)
        return policy

def dispatch_with_rl_and_optimizer(evs, batteries, flex_loads, price_forecast, carbon_forecast, transformer_limit, lambda_co2, mu_peak, horizon):
    env = FleetEnv(evs, price_forecast, carbon_forecast, transformer_limit)
    baseline_schedules = env.step_baseline()

    # RL agent trains quickly
    agent = QLearningAgent(horizon=horizon)
    agent.train(env, episodes=100)
    policy = agent.get_policy(price_forecast)

    # Use optimizer as safety layer: it guarantees SoC but we bias prices by policy
    # Modify price forecast according to policy: if policy says no charging (0), increase effective price
    adjusted_price = []
    for h, p in enumerate(price_forecast):
        act = policy[h] if h < len(policy) else 1
        if act == 0:
            adjusted_price.append(p*1.5)
        elif act == 1:
            adjusted_price.append(p*1.0)
        else:
            adjusted_price.append(p*0.7)

    # aggregate baseline for peak proxy - compute baseline aggregate
    baseline_agg = [0.0]*horizon
    for sched in baseline_schedules.values():
        for h in range(horizon):
            baseline_agg[h] += sched[h]

    ev_schedules = optimize_ev_fleet(evs, adjusted_price, carbon_forecast, transformer_limit, baseline_agg, lambda_co2, mu_peak, horizon)
    bat_schedules = optimize_batteries(batteries, adjusted_price, horizon)
    flex_schedules = optimize_flexible_loads(flex_loads, adjusted_price, horizon)

    # also compute baseline aggregate with batteries and flex as immediate
    # for simplicity baseline for other assets: same as optimized? We'll compute baseline ev only aggregated + zero for others baseline?
    baseline_total = baseline_agg.copy()
    # optimized aggregates
    optimized_agg = compute_aggregates(ev_schedules, bat_schedules, flex_schedules, horizon)

    # Ensure SoC guarantee 100% - check optimizer already ensures
    return {
        "baseline_ev": baseline_schedules,
        "ev_schedules": ev_schedules,
        "bat_schedules": bat_schedules,
        "flex_schedules": flex_schedules,
        "baseline_agg": baseline_total,
        "optimized_agg": optimized_agg,
        "policy": policy
    }
