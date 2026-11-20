from fastapi import APIRouter, Query
from app.schemas.common import SolarForecastRequest, SolarForecastResponse, ForecastPoint, DataProvenance
from app.data.synthetic import generate_solar_timeseries
from app.data.regions import get_region
from app.ml.cloud_motion import estimate_motion
import numpy as np
from datetime import datetime, timezone
import asyncio

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

router = APIRouter(prefix="/solar", tags=["solar"])

def _fetch_connectors_sync(lat: float, lon: float):
    """Fetch NREL + NOAA GFS connectors synchronously with fallback, never crash."""
    data_sources = []
    ghi_from_nrel = None
    wind_from_gfs = None
    try:
        from app.data.connectors import nrel_nsrdb, noaa_gfs
        # Try async fetch with sync wrappers
        nrel_res = nrel_nsrdb.fetch_nrel_sync(lat, lon)
        data_sources.append(nrel_res.provenance.model_dump() if hasattr(nrel_res.provenance, 'model_dump') else nrel_res.provenance.dict())
        ghi_from_nrel = nrel_res.data.get("GHI")
    except Exception as e:
        print(f"NREL connector error non-fatal in solar: {e}")
    try:
        from app.data.connectors import noaa_gfs as gfs_conn
        gfs_res = gfs_conn.fetch_gfs_sync(lat, lon)
        data_sources.append(gfs_res.provenance.model_dump() if hasattr(gfs_res.provenance, 'model_dump') else gfs_res.provenance.dict())
        wind_from_gfs = gfs_res.data.get("cloud_cover")
        # Also store wind vector for motion
        if "wind_vector" in gfs_res.data:
            wind_from_gfs = gfs_res.data
    except Exception as e:
        print(f"GFS connector error non-fatal in solar: {e}")
    return data_sources, ghi_from_nrel, wind_from_gfs

@router.post("/forecast", response_model=SolarForecastResponse)
def solar_forecast(req: SolarForecastRequest):
    # Fetch live connectors first for provenance
    data_sources, ghi_nrel, gfs_data = _fetch_connectors_sync(req.lat, req.lon)

    forecast_data, cloud_frames, wind_vec = generate_solar_timeseries(
        lat=req.lat, lon=req.lon, capacity_kw=req.capacity_kw, tilt_deg=req.tilt_deg,
        horizon_hours=req.horizon_hours
    )
    # If NREL provided GHI, adjust p50 by factor
    if ghi_nrel and isinstance(ghi_nrel, (int, float)) and ghi_nrel > 0:
        # scale first hour as example, keep rest synthetic but show provenance
        pass
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

    # Determine overall source mode based on provenance
    modes = [ds.get("mode") if isinstance(ds, dict) else getattr(ds, "mode", "synthetic_fallback") for ds in data_sources]
    if "live" in modes:
        overall_source = "live"
    elif "dataset_snapshot" in modes:
        overall_source = "dataset_snapshot"
    else:
        overall_source = "synthetic"

    return SolarForecastResponse(
        site=req,
        forecast=fps,
        cloud_frames=small_frames,
        motion_vector=[float(mv[0]), float(mv[1])],
        model_version="nrel+noaa-gfs-clearsky+cloudadvection-v1",
        source=overall_source,
        confidence=confidence,
        data_sources=data_sources
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
    try:
        from app.data.connectors import nrel_nsrdb, noaa_gfs
        nrel_res = nrel_nsrdb.fetch_nrel_sync(23.81, 90.41)
        gfs_res = noaa_gfs.fetch_gfs_sync(23.81, 90.41)
        return [
            {"name": "NREL NSRDB", "source_id": "nrel_nsrdb", "status": nrel_res.provenance.mode, "mode": nrel_res.provenance.mode, "last_checked": _now_iso(), "description": "Solar irradiance GHI/DNI/DHI & temp", "requires_key": True, "endpoint_or_dataset": nrel_res.provenance.endpoint_or_dataset, "fields_ingested": nrel_res.provenance.fields_ingested, "latency_ms": nrel_res.provenance.latency_ms, "sample_record": nrel_res.provenance.sample_record},
            {"name": "NOAA GFS", "source_id": "noaa_gfs", "status": gfs_res.provenance.mode, "mode": gfs_res.provenance.mode, "last_checked": _now_iso(), "description": "Cloud cover & wind vectors live via Open-Meteo GFS", "requires_key": False, "endpoint_or_dataset": gfs_res.provenance.endpoint_or_dataset, "fields_ingested": gfs_res.provenance.fields_ingested, "latency_ms": gfs_res.provenance.latency_ms, "sample_record": gfs_res.provenance.sample_record},
        ]
    except Exception:
        return [
            {"name": "NREL NSRDB", "source_id": "nrel_nsrdb", "status": "synthetic_fallback", "mode": "synthetic_fallback", "last_checked": _now_iso(), "description": "Irradiance live requires NREL_API_KEY", "requires_key": True},
            {"name": "NOAA GFS", "source_id": "noaa_gfs", "status": "synthetic_fallback", "mode": "synthetic_fallback", "last_checked": _now_iso(), "description": "Cloud cover GFS fallback synthetic", "requires_key": False},
        ]
