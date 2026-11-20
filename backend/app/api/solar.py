from fastapi import APIRouter, Query
from app.schemas.common import SolarForecastRequest, SolarForecastResponse, ForecastPoint
from app.data.synthetic import generate_solar_timeseries
from app.data.regions import get_region
from app.ml.cloud_motion import estimate_motion
import numpy as np
from datetime import datetime

router = APIRouter(prefix="/solar", tags=["solar"])

@router.post("/forecast", response_model=SolarForecastResponse)
def solar_forecast(req: SolarForecastRequest):
    forecast_data, cloud_frames, wind_vec = generate_solar_timeseries(
        lat=req.lat, lon=req.lon, capacity_kw=req.capacity_kw, tilt_deg=req.tilt_deg,
        horizon_hours=req.horizon_hours
    )
    # convert to ForecastPoint models
    fps = []
    for f in forecast_data:
        fps.append(ForecastPoint(
            timestamp=f["timestamp"],
            p10=f["p10"],
            p50=f["p50"],
            p90=f["p90"],
            variability_index=f["variability_index"]
        ))
    # estimate motion vector from first two frames if available
    try:
        if len(cloud_frames)>=2:
            mv = estimate_motion(cloud_frames[0], cloud_frames[1])
        else:
            mv = (wind_vec[0], wind_vec[1])
    except:
        mv = (float(wind_vec[0]), float(wind_vec[1]))

    # convert cloud_frames to list-of-list for JSON (downsample)
    # take 5 frames max, downsample to 16x16
    small_frames = []
    for cf in cloud_frames[:5]:
        # downsample
        if cf.shape[0] > 16:
            # simple averaging
            step = cf.shape[0] // 16
            small = cf[::step, ::step][:16,:16]
        else:
            small = cf
        small_frames.append(small.tolist())

    # confidence heuristic
    avg_var = float(np.mean([f["variability_index"] for f in forecast_data]))
    confidence = float(max(0.6, min(0.98, 1.0 - avg_var*0.3)))

    return SolarForecastResponse(
        site=req,
        forecast=fps,
        cloud_frames=small_frames,
        motion_vector=[float(mv[0]), float(mv[1])],
        model_version="synthetic-clearsky+cloudadvection-v1",
        source="synthetic",
        confidence=confidence
    )

@router.get("/forecast", response_model=SolarForecastResponse)
def solar_forecast_get(
    lat: float = 23.8103,
    lon: float = 90.4125,
    capacity_kw: float = 500,
    tilt_deg: float = 23,
    horizon_hours: int = 24
):
    req = SolarForecastRequest(lat=lat, lon=lon, capacity_kw=capacity_kw, tilt_deg=tilt_deg, horizon_hours=horizon_hours)
    return solar_forecast(req)

@router.get("/integrations")
def solar_integrations():
    return [
        {"name": "NREL NSRDB", "status": "synthetic", "last_checked": datetime.utcnow().isoformat(), "description": "Irradiance live requires NREL_API_KEY", "requires_key": True},
        {"name": "NOAA GFS", "status": "synthetic", "last_checked": datetime.utcnow().isoformat(), "description": "Cloud cover GFS fallback synthetic", "requires_key": False},
    ]
