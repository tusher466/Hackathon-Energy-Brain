from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Optional
from datetime import datetime, timezone
import time

class DataProvenance(BaseModel):
    source_id: str  # nrel_nsrdb | noaa_gfs | electricity_maps | opsd | pjm_dataminer
    source_name: str
    mode: Literal["live", "dataset_snapshot", "synthetic_fallback"]
    endpoint_or_dataset: str
    region_scope: str  # e.g. "Global", "BD, DE, US", "DE", "US-PJM"
    fields_ingested: List[str]
    fetched_at: str  # ISO UTC
    latency_ms: float
    sample_record: Dict[str, Any]  # small sanitized dict
    status_code: Optional[int] = None
    description: Optional[str] = None

class ConnectorResult(BaseModel):
    data: Dict[str, Any]  # parsed payload normalized
    provenance: DataProvenance
    raw_sample: Optional[Dict[str, Any]] = None

def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def measure_latency(start: float) -> float:
    return round((time.perf_counter() - start) * 1000.0, 2)
