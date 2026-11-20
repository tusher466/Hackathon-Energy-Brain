from fastapi import APIRouter
from app.schemas.common import DemandForecastRequest, DemandForecastResponse, ForecastPoint
from app.data.synthetic import generate_demand_timeseries
from app.data.regions import get_region
from app.ml.demand_transformer import demand_forecaster
import numpy as np
from datetime import datetime, timedelta

router = APIRouter(prefix="/demand", tags=["demand"])

@router.post("/forecast", response_model=DemandForecastResponse)
def demand_forecast(req: DemandForecastRequest):
    synthetic = generate_demand_timeseries(req.region_code, req.sites, req.horizon_hours)
    # For ML model: we need historical (we generate 168h history)
    history_h = 168
    hist_data = generate_demand_timeseries(req.region_code, req.sites, history_h, start_dt=datetime.utcnow()-timedelta(hours=history_h))
    hist_timestamps = [datetime.utcnow()-timedelta(hours=history_h-i) for i in range(history_h)]
    # but we already have synthetic list? Use synthetic from history
    hist_loads = [h["p50"] for h in hist_data]
    hist_temps = [25 + 5*np.sin(2*np.pi*(i%24)/24) + np.random.normal(0,1) for i in range(history_h)]
    # run forecaster
    forecasts, feat_imp, mape, pinball = demand_forecaster.forecast(hist_timestamps, hist_loads, hist_temps, req.horizon_hours)

    fps = []
    for f in forecasts:
        fps.append(ForecastPoint(
            timestamp=f["timestamp"],
            p10=f["p10"],
            p50=f["p50"],
            p90=f["p90"],
            variability_index=f.get("variability_index")
        ))

    return DemandForecastResponse(
        region_code=req.region_code,
        forecast=fps,
        feature_importance=feat_imp,
        backtest_mape=mape,
        backtest_pinball=pinball,
        source="synthetic",
        model_version=demand_forecaster.version
    )

@router.get("/forecast", response_model=DemandForecastResponse)
def demand_forecast_get(region_code: str = "BD", sites: int = 3, horizon_hours: int = 48):
    req = DemandForecastRequest(region_code=region_code, sites=sites, horizon_hours=horizon_hours)
    return demand_forecast(req)
