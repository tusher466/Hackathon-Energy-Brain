# Energy Brain – Smart Energy Optimization & Demand-Response Platform

**One decision loop: Forecast → Uncertainty → Optimize → Act → Explain → Measure**

Energy Brain fuses solar forecast, demand forecast, grid carbon/price, then dispatches EV+battery+flexible loads as VPP. Every decision ships with plain-language reason, counterfactual, confidence band. Headline metric always money saved, CO₂ avoided, peak kW shaved.

## Quick Start – One command per side (offline-first synthetic fallback)

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173

**Docker**
```bash
docker-compose up --build
```

**Makefile**
```bash
make install
make backend   # terminal 1
make frontend  # terminal 2
make test      # pytest + frontend build
```

All data works OFFLINE with realistic synthetic generators. Live connectors (NREL, NOAA, ElectricityMaps, OPSD, PJM) auto fallback to synthetic when no API key.

## Modules – All Real Working

- **Solar Forecast Studio** `/solar`: clear-sky geometry × cloud transmission 32×32 advected by wind vector. Motion estimated via phase correlation FFT (numpy) fallback block matching. Output P10/P50/P90 + variability index + cloud frames animation.
- **Demand Forecast** `/demand`: multi-site hourly load weekday/weekend, temp sensitivity, economic indicator. Compact Transformer encoder fallback sklearn GB quantile. Feature importance, MAPE, pinball.
- **VPP Dispatch** `/vpp`: fleet simulator N EVs arrival/departure SoC required, M batteries, flexible loads. Baseline immediate vs Smart RL tabular Q-learning + LP safety linprog (scipy) guarantees SoC 100%. Sliders λ CO₂, μ peak, transformer limit. Side-by-side cost/CO₂/peak, fairness metrics.
- **Grid Operator Copilot** `/grid`: scenario engine (cloud collapse, wind lull, line trip, cyber outage) deterministic 6-step recovery: cranking, bus energize, load pickup, freq/volt checks. SVG network re-energize animation. Copilot chat RAG over local `backend/app/knowledge/*.md` TF-IDF, citations + referenced steps. LLM never controls grid.
- **Panel Health Inspector** `/panels`: upload drone thermal or use synthetic samples generated at startup. OpenCV normalize, threshold hot, contours, classify defect by shape/temp delta (hotspot, bypass diode, soiling, string fault). Annotated image, efficiency loss %, yearly kWh + money loss per region (BDT/EUR/USD).
- **Carbon & Cost Ledger** `/ledger`: SQLite via SQLAlchemy logs every decision. Dashboard cumulative, by module/region, marginal vs average methodology selectable, CSV export + printable report.
- **Region Profiles** `BD, DE, US-PJM`: config-driven tariff, currency, carbon factors, peak hours, voltage. Switching changes everywhere instantly.

## Design Direction – Control Room at Dusk

Avoid: purple/blue-violet gradients, neon glows, glassmorphism, emojis, sparkle, robot imagery, Inter everywhere, marketing phrases.

Use: warm neutrals (ink-950 #0D1210, ink-900 #131A17, bone-50 #F6F3EC), text fg-strong #ECE8DD / #141A17, primary amber #E0A73A signal, secondary moss #5F8F6B, slate teal #3E7C86 cool counterpoint, brick #C2503A alert. 60% neutrals, 30% secondary, 10% accent. Amber only most important per screen. Headings Fraunces/Newsreader serif, UI Instrument Sans/Geist, numbers JetBrains Mono tabular. Hairline 1px borders, 8-12px radii, 3% film grain, thin chart lines, annotated peaks. Motion 200-400ms ease-out.

Copy tone precise calm operational: "Charge 42 EVs between 01:00 and 04:30. Saves 118 USD. Confidence 91%."

## Premium Features Checklist (All Exist)

1. Live demo Simulate a day button plays 24h in 60s across modules with scrubber – Overview + SSE `/api/v1/simulate/day`
2. Scenario compare – save two configs side-by-side delta KPIs (local comparison in VPP)
3. Counterfactual explainer every decision – VPP explain counterfactual + Solar/Demand Explain drawer
4. Uncertainty bands everywhere P10/P50/P90 + confidence label
5. Region switch real currency/tariff/carbon instant
6. Human-in-loop approvals queue approve/reject logged – Overview + Ledger
7. Savings ledger methodology tooltip + export CSV + printable
8. Black-start timeline step-by-step network re-energization SVG animation
9. Thermal inspection annotated overlay + money loss estimate per region
10. Command palette Cmd+K, keyboard nav, dark/light, print report
11. API docs embedded OpenAPI + Integrations page showing live vs synthetic provenance
12. Seed data + one-click Load demo dataset (default fleet, synthetic samples) + Reset ledger

## Backend Architecture

```
backend/
  app/
    main.py            # app factory, CORS, routers, lifespan warm models, SSE simulate
    core/config.py     # pydantic-settings .env
    core/db.py         # SQLAlchemy SQLite
    api/               # solar, demand, vpp, grid, panels, ledger, regions, health
    services/          # ledger, grid_service (RAG, plan)
    ml/                # solar_lstm, demand_transformer, rl_agent, optimizer (linprog), cloud_motion, thermal
    data/              # synthetic generators, regions
    schemas/           # pydantic v2
    knowledge/         # markdown docs RAG
  tests/               # pytest: solar, demand, vpp, thermal
  requirements.txt
```
Typed responses, OpenAPI tags, versioned `/api/v1`, SSE/WebSocket streaming, request ID logging.

## Frontend Architecture

```
frontend/
  src/
    app/router.tsx     # React Router layout + routes, 404
    components/        # Layout, KPIStrip, Chart
    pages/             # Overview, Solar, Demand, VPP, Grid, Panels, Ledger, Trust, Settings
    lib/api.ts         # fetch client
    lib/format.ts      # currency/units by region
    state/useStore.ts  # zustand region + dark
```
Libraries: react-router-dom, tanstack react-query, recharts, framer-motion (subtle), lucide-react icons, zustand. Routes `/`, `/solar`, `/demand`, `/vpp`, `/grid`, `/panels`, `/ledger`, `/trust`, `/settings`. Overview hero KPI strip, decision timeline, live asset map/flow diagram. Command palette, light/dark.

## Docs

- `docs/ARCHITECTURE.md` – workflow mermaid input→processing→output, model selection why, fallbacks, explainability
- `docs/BUSINESS.md` – value prop, SaaS tiers per-asset-per-month + % verified savings, adoption path commercial→aggregator→utility, cross-border BD/EU/US, market validation hypotheses pilot KPIs
- `docs/IMPACT.md` – KPIs cost saved %, CO₂ t/yr, peak %, MAPE, SoC 100%, responsible AI bias mitigation, privacy
- `docs/DEMO_SCRIPT.md` – 3-min demo exact click path + talking points how to explain each AI decision
- `docs/SCALING.md` – modular services, cloud deployment containers stateless API Postgres/Timescale, queue training, standards IEC61850/IEEE2030.5/OpenADR, global contributor integration

## Quality Bar

- pytest 7 tests passing: SoC guarantee never violated, bands monotonic P10≤P50≤P90, cloud motion error <2px on synthetic shifts, demand monotonic, forecaster training, thermal defects.
- Frontend `npm run build` passes no TS errors, no console errors.
- Lazy loading routes, skeletons, no layout shift on charts.

## Business

See `docs/BUSINESS.md` for SaaS tiers, adoption, cross-border.

## Run Verification (done)

- Backend tests: `python -m pytest tests -v` – 7 passed
- Frontend build: `npm run build` – 742kB gzip 210kB built
- No placeholder text, every button does something
- Offline-first synthetic works without keys

## Environment Keys (optional)

Create `backend/.env`:
```
NREL_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
ELECTRICITYMAPS_API_KEY=
```

If missing, app auto uses synthetic and flags source synthetic honestly.

---

Built as hackathon complete runnable project – no TODO stubs.
