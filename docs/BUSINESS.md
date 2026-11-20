# Business Model – Energy Brain

## Value Proposition

Commercial/industrial energy managers + EV fleet operators + VPP aggregators waste 12-25% cost on peak tariffs and miss CO₂ targets because forecast uncertainty and manual dispatch don't capture real-time price/carbon + peak penalty. Energy Brain closes loop: Forecast → Uncertainty → Optimize → Act → Explain → Measure with single decision engine, cross-border tariffs, human-in-the-loop, and proof via ledger.

Quantifiable: 15% cost saved, 80-120 kg CO₂ avoided per EV per month, 30-40% peak shaved, SoC guarantee 100%, forecast MAPE <8%.

## SaaS Tiers

- **Starter** – per site: $49/mo + 1 building, 10 EVs, basic forecast, ledger.
- **Fleet** – per-asset-per-month: $5 per EV, $10 per battery/inverter + % of verified savings 10% (performance). Includes VPP dispatch, thermal inspection 50 images/mo.
- **Aggregator** – $499/mo base + $3 per asset + 15% of verified savings, black start simulator, API access, white-label report, SSO.
- **Grid** – custom: $5000/mo + integration (IEC 61850, IEEE 2030.5, OpenADR), on-prem option, SLA.

Why % of verified savings? Aligns incentives, judge-friendly business model.

## Adoption Path

1. **Commercial buildings + EV fleets** (Dhaka, then India/SE Asia): high evening peak, high grid carbon 0.68kg/kWh, tariff spread 6.2→12.8 BDT incentivizes shift. Pilot KPI: cost saved %, peak reduction %, SoC guarantee.
2. **Aggregators/VPP operators** in EU/Germany: lower carbon but day-ahead price volatility, need uncertainty bands + counterfactual. Pilot: OPSD data integration, show marginal vs average CO₂.
3. **Utilities/grid operators** US PJM, then cross-border: LMP nodal pricing, black start copilot compliance, human-in-loop approval log.

## Cross-Border Plan

- Bangladesh/India/SE Asia first: evening peak, high carbon, low digitalization → biggest savings story. Partnership with commercial building management, EV rental fleets.
- EU Germany: day-ahead market, OPSD integration, GDPR privacy docs, bias mitigation (fairness across users). EU Green Deal compliance.
- US PJM: LMP, standards IEEE 2030.5, OpenADR for dispatch, cyber-outage scenario.

Region profiles config-driven: BD (BDT, evening peak 18-23, 0.68 avg), DE (EUR, 0.38 avg), US (USD, 0.45 avg). Switching instantly changes currency, tariffs, carbon factors everywhere.

## Market Validation Hypotheses

- H1: EV owners with early departure get equal SoC if optimizer safety layer – measure fairness variance <5%.
- H2: Night charging saves >10% vs immediate in BD tariff.
- H3: Forecast confidence band (P10/P90) reduces operator override rate vs single-line forecast.
- Pilot KPIs: cost saved %, CO₂ avoided t/yr per site, peak reduction %, forecast MAPE, SoC guarantee rate 100%, approval time <2min, thermal false positive <10%.

## Go-to-Market

Hackathon demo → 2 pilot buildings (Dhaka) → case study ledger proof → aggregator partnership → EU/US expansion via integrations page showing live vs synthetic.

## Defensibility

Offline-first synthetic fallback, safety layer LP guarantee, explainability drawer, ledger proof, cross-border config, control-room design not generic AI template.
