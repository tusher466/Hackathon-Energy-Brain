# EV Fleet Dispatch Guidelines

## Constraints
- Arrival SoC 20-50%, required departure SoC 80% minimum
- Max charge 7kW (AC) or 50kW DC
- Transformer limit 1000kW feeder
- Battery cycle limit: 1 cycle/day recommended

## Cost Optimization
Minimize cost = price * energy + lambda*CO2 + mu*peak
- lambda default 0.5 (BD high carbon = 0.7, EU lower 0.3)
- mu = 1.0 emphasizes peak shaving

## Fairness
All EVs must achieve required SoC by departure (100% SoC guarantee). No user penalized by early departure time - check fairness metrics: SoC delivery variance <5%.
If early departure EV gets lower SoC in optimization, fallback to baseline immediate charging for that EV.

## Safety Layer
Rolling horizon optimizer (linprog) ensures feasibility even if RL policy fails. RL only biases price threshold.

## Human Approval
Operator sees cost saved, CO2 saved, peak reduction before approval. Approval queue logs decision.

## Regional Tariffs
- BD: BDT 6.2 night, 8.5 day, 12.8 peak. Peak hours 18-23
- DE: EUR 0.24 night, 0.32 day, 0.42 peak. Peak 8-10,17-19
- US: USD 0.08 night, 0.15 day, 0.28 peak. Peak 14-19

