from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class RegionProfile(BaseModel):
    code: str
    name: str
    currency: str
    currency_symbol: str
    tariff_structure: str
    peak_hours: List[int]
    carbon_factor_avg_kg_per_kwh: float
    carbon_factor_marginal_kg_per_kwh: float
    price_per_kwh_day: float
    price_per_kwh_night: float
    price_per_kwh_peak: float
    voltage_level: str
    description: str

class ForecastPoint(BaseModel):
    timestamp: datetime
    p10: float
    p50: float
    p90: float
    variability_index: Optional[float] = None

class SolarForecastRequest(BaseModel):
    lat: float = 23.8103
    lon: float = 90.4125
    capacity_kw: float = 500.0
    tilt_deg: float = 23.0
    horizon_hours: int = 24

class SolarForecastResponse(BaseModel):
    site: SolarForecastRequest
    forecast: List[ForecastPoint]
    cloud_frames: List[List[List[float]]]  # simplified representation
    motion_vector: List[float]
    model_version: str
    source: Literal["synthetic", "live"]
    confidence: float

class DemandForecastRequest(BaseModel):
    region_code: str = "BD"
    sites: int = 3
    horizon_hours: int = 48
    include_temperature: bool = True

class DemandForecastResponse(BaseModel):
    region_code: str
    forecast: List[ForecastPoint]
    feature_importance: dict
    backtest_mape: float
    backtest_pinball: float
    source: Literal["synthetic", "live"]
    model_version: str

class EVAsset(BaseModel):
    id: str
    arrival_hour: int
    departure_hour: int
    initial_soc_kwh: float
    required_soc_kwh: float
    capacity_kwh: float
    max_charge_kw: float

class BatteryAsset(BaseModel):
    id: str
    capacity_kwh: float
    initial_soc_kwh: float
    max_charge_kw: float
    max_discharge_kw: float
    efficiency: float = 0.92

class FlexibleLoad(BaseModel):
    id: str
    power_kw: float
    flexible_hours: List[int]
    duration_hours: int = 2

class VPPDispatchRequest(BaseModel):
    region_code: str = "BD"
    evs: List[EVAsset]
    batteries: List[BatteryAsset]
    flexible_loads: List[FlexibleLoad]
    lambda_co2: float = 0.5
    mu_peak: float = 1.0
    transformer_limit_kw: float = 1000.0
    price_forecast: Optional[List[float]] = None
    carbon_forecast: Optional[List[float]] = None
    horizon_hours: int = 24

class VPPDispatchResponse(BaseModel):
    baseline_cost: float
    optimized_cost: float
    cost_saved: float
    co2_saved_kg: float
    peak_before_kw: float
    peak_after_kw: float
    peak_reduction_kw: float
    ev_schedules: dict
    battery_schedules: dict
    flexible_schedules: dict
    aggregate_before: List[float]
    aggregate_after: List[float]
    explain: dict
    fairness_metrics: dict

class GridEvent(BaseModel):
    type: str
    hour: int
    severity: str
    description: str

class GridRecoveryStep(BaseModel):
    step_id: int
    action: str
    energized_nodes: List[str]
    frequency_hz: float
    voltage_pu: float
    load_mw: float
    timestamp: str
    status: str

class BlackStartRequest(BaseModel):
    region_code: str = "BD"
    scenario: str = "cloud_collapse"
    # scenario: cloud_collapse, wind_lull, line_trip, cyber_outage

class BlackStartResponse(BaseModel):
    scenario: str
    events: List[GridEvent]
    recovery_plan: List[GridRecoveryStep]
    network_graph: dict
    estimated_recovery_minutes: int

class CopilotQuery(BaseModel):
    question: str
    scenario: str = "cloud_collapse"
    region_code: str = "BD"

class CopilotResponse(BaseModel):
    answer: str
    citations: List[str]
    referenced_steps: List[int]
    source: Literal["llm", "rule_based"]

class PanelDefect(BaseModel):
    id: str
    type: str
    severity: str
    bbox: List[int]
    temp_delta_c: float
    efficiency_loss_pct: float
    yearly_loss_kwh: float
    money_loss: float
    recommendation: str

class PanelInspectionResponse(BaseModel):
    defects: List[PanelDefect]
    annotated_image_b64: Optional[str] = None
    total_efficiency_loss_pct: float
    total_yearly_loss_kwh: float
    total_money_loss: float
    summary: str

class LedgerEntry(BaseModel):
    id: int
    timestamp: datetime
    module: str
    action: str
    cost_saved: float
    co2_avoided_kg: float
    peak_shaved_kw: float
    region_code: str
    details: dict

class LedgerSummary(BaseModel):
    total_cost_saved: float
    total_co2_avoided_kg: float
    total_peak_shaved_kw: float
    total_entries: int
    by_module: dict
    by_region: dict
    currency: str

class ApprovalItem(BaseModel):
    id: str
    timestamp: datetime
    action: str
    module: str
    description: str
    status: str
    kpi_impact: dict

class IntegrationStatus(BaseModel):
    name: str
    status: Literal["live", "synthetic", "offline"]
    last_checked: datetime
    description: str
    requires_key: bool

class ModelStatus(BaseModel):
    name: str
    version: str
    status: str
    trained_at: Optional[datetime] = None
    accuracy: Optional[float] = None
