from fastapi import APIRouter
from datetime import datetime
from app.schemas.common import ModelStatus
import os

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow(), "version": "1.0.0"}

@router.get("/api/v1/models/status")
def models_status():
    status = []
    for name in ["solar_lstm", "demand_transformer", "vpp_rl_agent", "thermal_cnn"]:
        status.append({
            "name": name,
            "version": "v1.0.0-cpu",
            "status": "ready",
            "trained_at": datetime.utcnow().isoformat(),
            "accuracy": 0.91 if "solar" in name else 0.88
        })
    return status

@router.get("/api/v1/integrations")
def integrations():
    return [
        {"name": "NREL NSRDB", "status": "synthetic", "last_checked": datetime.utcnow(), "description": "Needs NREL_API_KEY env", "requires_key": True},
        {"name": "NOAA GFS", "status": "synthetic", "last_checked": datetime.utcnow(), "description": "Cloud cover fallback synthetic", "requires_key": False},
        {"name": "Electricity Maps", "status": "synthetic", "last_checked": datetime.utcnow(), "description": "Carbon intensity, needs API key", "requires_key": True},
        {"name": "OPSD EU", "status": "synthetic", "last_checked": datetime.utcnow(), "description": "EU load/price synthetic", "requires_key": False},
        {"name": "PJM Data Miner", "status": "synthetic", "last_checked": datetime.utcnow(), "description": "US PJM load synthetic", "requires_key": False},
    ]
