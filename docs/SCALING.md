# Scaling – Energy Brain

## Modular Services

Current monolith FastAPI can split:

- `forecast-service` (solar + demand) – GPU optional, scales horizontally.
- `dispatch-service` (VPP RL+LP) – CPU heavy linprog, queue via Celery.
- `grid-service` (black start simulation) – deterministic, stateless.
- `thermal-service` (OpenCV) – GPU optional, S3 image store.
- `ledger-service` – SQLite now, swap to Postgres/TimescaleDB for time-series.
- `copilot-service` – LLM RAG, vector DB (pgvector / Qdrant).

All APIs versioned `/api/v1`, typed Pydantic, OpenAPI.

## Cloud Deployment

- Containers: Dockerfile for backend (python 3.11 slim), frontend nginx multi-stage.
- Stateless API: 12-factor, env keys from secrets manager.
- Persistence: Postgres/TimescaleDB for forecasts (partition by region/month), S3 for thermal images, Redis for SSE pubsub.
- Queue: Celery/RQ for training jobs (nightly retrain LSTM/Transformer 168h history).
- Observability: OpenTelemetry traces per request ID, Prometheus metrics forecast latency, dispatch solve time.
- CI: pytest + frontend build gate.

## Standards

- **IEC 61850**: grid substation modeling, Goose messages for trip signals – map network_graph to SCL.
- **IEEE 2030.5**: DER (EV, battery, PV) dispatch via REST – VPP schedules export as 2030.5 DERProgram.
- **OpenADR**: price signals for demand response – price_forecast input compatible.
- **SunSpec**: PV inverter modbus – solar forecast API.

## Global Contributor Integration

- Region profiles JSON config – contributors add new region (e.g., India, Kenya) via PR adding tariff + carbon.
- Knowledge base markdown: contributors add black-start procedures per country.
- Connector stubs with same schema – add live implementation keeping fallback.
- Frontend translations: instrument using format.ts currency/symbol abstraction.

## Performance

- Forecast: <200ms for 24h horizon synthetic, <1s with live GFS fetch + cache 10min rate-limit.
- VPP dispatch: linprog HiGHS ~50ms for 6 EVs ×24h =144 vars, scales to 100 EVs ×96h quarter-hour =9600 vars – use cvxpy or OR-Tools for larger, decompose per feeder.
- Thermal: OpenCV ~100ms per 640×480 image.

## Security

- No personal data, EV IDs anonymized, aggregate only.
- API key handling: .env not committed, synthetic fallback if missing.
- Approval queue ensures human-in-loop – no direct breaker control.
- CORS configured.

## Roadmap

- Phase 1: Dhaka pilot 2 buildings + 20 EVs, ledger proof.
- Phase 2: Aggregator API, OPSD/NREL live, timeseries DB.
- Phase 3: Grid operator license, IEC 61850 integration, on-prem.
