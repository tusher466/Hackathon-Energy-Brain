# Demo Script – 3 Minute

**Setup**: backend running `uvicorn app.main:app --reload` port 8000, frontend `npm run dev` port 5173, seed data loaded (ledger auto seed).

## 0:00-0:20 Overview – Hook

"Energy Brain is ONE decision loop: Forecast → Uncertainty → Optimize → Act → Explain → Measure. Not 5 separate demos. Every decision ships with money saved, CO₂ avoided, peak shaved, confidence band, counterfactual."

Click path: `/` Overview

Talking points:
- KPI strip: Saved today, CO₂ avoided, Peak shaved, Forecast error. Show region switch BD→DE→US changes currency instantly. Cross-border day one.
- Next 24h decision timeline: Solar P50 vs Demand P50, variability index.
- Live asset map flow diagram: PV 500kW, Batt 150kWh, Grid → EMS Bus Decision Engine → EV Fleet 42, Industrial, HVAC.
- Human-in-loop approvals queue: Approve EV shift 01-04:30 saves 118 USD, confidence 91%.
- Click "Simulate a day (60s)" – SSE streams 24h in 60 sec, chart updates live, scrubber works. "If immediate charging, +18% cost and +210kW peak."

## 0:20-0:50 Solar Forecast Studio

Route `/solar`

Action: Show site params lat/lon Dhaka, capacity 500kW, tilt 23°, horizon 24h. Click Run forecast.

Explain: "Clear-sky model solar geometry × cloud transmission field 32×32 advected by wind vector. Motion vector estimated via phase correlation FFT – see vector [0.8, -1.2]. Cloud frames animate." Point to variability index chart.

AI decision explain: Top drivers: solar zenith, cloud transmission 0.78. Counterfactual: without motion prediction, error 18% MAPE, with 7.8%.

## 0:50-1:10 Demand Forecast

Route `/demand`

Action: Switch region BD→DE, click Run.

Explain: "Multi-site load with weekday/weekend, temperature sensitivity regional. Model compact Transformer encoder fallback sklearn GB quantile. Feature importance shows lag24 dominates, hour sin/cos, temp high in BD. Backtest MAPE 8.2% pinball 0.124. P10≤P50≤P90 guaranteed."

## 1:10-1:50 VPP Dispatch

Route `/vpp`

Action: Show fleet 6 EVs arrival/departure SoC. Adjust λ CO₂ slider 0.5→1.5, μ peak 1→2. Click Run Smart Dispatch.

Explain: "Two controllers side-by-side: baseline immediate vs smart RL+LP. RL tabular Q-learning learns price threshold online, LP safety linprog guarantees SoC 100%. Hard constraints transformer 1000kW, SoC bounds, departure deadlines."

Point to KPIs: Cost saved ৳ X, CO₂ saved Y kg, peak reduction Z kW. Chart aggregate before vs after. Per-EV schedule visualization █ for charging. Fairness check variance 0.02, all guaranteed. Counterfactual drawer: top drivers price spread, carbon peak at hour X, peak penalty mu reduces Z kW.

Ledger auto logs.

## 1:50-2:20 Grid Operator Copilot • Black Start

Route `/grid`

Action: Select scenario Cloud Collapse, click Load recovery plan.

Explain: "Scenario engine synthetic renewable failure. Deterministic recovery 6 steps: cranking source hydro 00:05, energize bus S1+ batt, crank gas 00:28, pickup critical industrial 5MW 00:45 (frequency 49.8Hz), commercial+EV delayed until stable 01:15, residential 01:50 full. Network SVG re-energizes step-by-step, freq/volt/load shown."

Copilot: Type "How to handle EV during black start?" → Ask. Answer cites black_start_procedure.md and step 5, shows citations, referenced steps. Badge: LLM never controls grid, operator approves.

## 2:20-2:35 Panel Health Inspector

Route `/panels`

Action: Click New synthetic sample, show annotated image with boxes.

Explain: "Drone thermal: OpenCV normalize, threshold hot, contours, classify by shape/temp delta: hotspot cell, bypass diode, soiling, string fault. Output annotated overlay + yearly kWh loss + money loss in BDT/EUR/USD per region. Example: 5 defects, 12% loss, ৳ 1,200/yr."

Upload button works.

## 2:35-2:55 Ledger + Trust

Route `/ledger`

Action: Show totals, methodology tooltip marginal vs average. Export CSV, printable report. "Proof: every decision logged SQLite."

Route `/trust`

Quick: Data provenance, bias fairness SoC variance, failure modes, privacy, model selection why LSTM/Transformer/RL+LP/LLM+RAG.

## 2:55-3:00 Settings & Closing

Route `/settings`

Show region switch tariff hourly 24h view, model status ready, integrations live vs synthetic provenance, API docs link, premium checklist all exist.

Copy close: "Control room at dusk design – warm neutrals + amber signal only for most important, no purple gradients, no sparkle icons, precise calm operational copy. One command to start each side, Docker ready, tests passing, fully offline synthetic."

## How to explain each AI decision talking points

- Solar: confidence from variability index std cloud field, motion vector phase correlation.
- Demand: feature importance, backtest metrics holdout.
- VPP: top drivers price/carbon/peak slider, fairness guarantee.
- Grid: citations + steps, human approval.
- Panels: shape classification heuristic + temp delta.
- All: data sources + model version + counterfactual.

## Commands

Backend: `uvicorn app.main:app --reload` in `backend/`
Frontend: `npm run dev` in `frontend/`
Docker: `docker-compose up`
Makefile: `make dev`, `make test`
