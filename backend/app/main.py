from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
import os

from app.core.config import get_settings
from app.core.db import init_db
from app.api import solar, demand, vpp, grid, panels, ledger, regions, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing DB and models...")
    init_db()
    try:
        from app.ml.solar_lstm import solar_forecaster
        from app.ml.demand_transformer import demand_forecaster
        print(f"Torch available for solar: checked")
        print("Models warmed")
    except Exception as e:
        print(f"Model warm error: {e}")
    yield
    print("Shutdown")

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Energy Brain - smart energy optimization and demand-response platform",
    lifespan=lifespan
)

# CORS
origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (API)
app.include_router(health.router)
app.include_router(solar.router, prefix=settings.api_v1_prefix)
app.include_router(demand.router, prefix=settings.api_v1_prefix)
app.include_router(vpp.router, prefix=settings.api_v1_prefix)
app.include_router(grid.router, prefix=settings.api_v1_prefix)
app.include_router(panels.router, prefix=settings.api_v1_prefix)
app.include_router(ledger.router, prefix=settings.api_v1_prefix)
app.include_router(regions.router, prefix=settings.api_v1_prefix)

# --- Frontend static handling (for single-service Render deploy) ---
def find_frontend_dist():
    candidates = [
        Path(__file__).parent.parent / "frontend" / "dist",      # ./backend/frontend/dist (docker multi-stage)
        Path(__file__).parent.parent.parent / "frontend" / "dist",  # project root frontend/dist
        Path("/app/frontend/dist"),                               # production copy
        Path("/app/frontend_dist"),                               # alternative
        Path(__file__).parent / "static" / "frontend",            # ./app/static/frontend
        Path("frontend/dist"),                                    # relative
        Path("static"),                                           # ./static from root Dockerfile
        Path("dist"),                                             # ./dist
        Path(__file__).parent.parent / "static",                 # ./backend/static
    ]
    for p in candidates:
        if p.exists() and (p / "index.html").exists():
            return p.resolve()
        # also check if p itself is dist with index
        if p.is_dir() and (p / "index.html").exists():
            return p.resolve()
    return None

frontend_dist = find_frontend_dist()

# Define /api info BEFORE mounting frontend so it takes precedence
@app.get("/api")
def api_info():
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "api_prefix": settings.api_v1_prefix,
        "message": "Energy Brain API - control room at dusk. Forecast -> Optimize -> Act -> Explain -> Measure",
        "frontend": f"served from {frontend_dist}" if frontend_dist else "not bundled, build frontend"
    }

if frontend_dist:
    print(f"Found frontend dist at {frontend_dist}, mounting static files for full-stack deploy")
    # Mount assets if exists (vite puts assets in /assets)
    assets_path = frontend_dist / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

    # Mount root static with html=True for SPA fallback (serves index.html for unknown routes)
    # API routes defined above take precedence
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    print("Frontend dist not found, serving API only mode")
    @app.get("/")
    def root():
        return {
            "name": settings.app_name,
            "version": settings.version,
            "docs": "/docs",
            "api_prefix": settings.api_v1_prefix,
            "message": "Energy Brain API - control room at dusk. Forecast -> Optimize -> Act -> Explain -> Measure",
            "note": "Frontend not bundled. Deploy frontend separately or build it (npm run build in frontend/)"
        }

# For sse simulation endpoint
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime, timedelta
import random

@app.get("/api/v1/simulate/day")
async def simulate_day(region_code: str = "BD"):
    """
    Simulate 24h in ~60 seconds via SSE.
    """
    async def event_generator():
        from app.data.synthetic import generate_solar_timeseries, generate_demand_timeseries, generate_price_carbon_forecasts
        solar_fc, _, _ = generate_solar_timeseries(23.8, 90.4, 500, 23, 24)
        demand_fc = generate_demand_timeseries(region_code, 3, 24)
        price, carbon = generate_price_carbon_forecasts(region_code, 24)
        for h in range(24):
            data = {
                "hour": h,
                "solar_p50": solar_fc[h]["p50"] if h < len(solar_fc) else 0,
                "demand_p50": demand_fc[h]["p50"] if h < len(demand_fc) else 0,
                "price": price[h],
                "carbon": carbon[h],
                "timestamp": (datetime.utcnow() + timedelta(hours=h)).isoformat()
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(2)
        yield f"data: {json.dumps({'done': True})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
