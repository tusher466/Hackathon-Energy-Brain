from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.core.db import Base
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List

class LedgerEntryDB(Base):
    __tablename__ = "ledger"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    module = Column(String)
    action = Column(String)
    cost_saved = Column(Float)
    co2_avoided_kg = Column(Float)
    peak_shaved_kw = Column(Float)
    region_code = Column(String)
    details_json = Column(JSON, default=dict)

class ApprovalDB(Base):
    __tablename__ = "approvals"
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String)
    module = Column(String)
    description = Column(String)
    status = Column(String, default="pending")
    kpi_impact_json = Column(JSON, default=dict)

def log_entry(db: Session, module: str, action: str, cost_saved: float, co2_kg: float, peak_kw: float, region_code: str, details: dict):
    entry = LedgerEntryDB(
        module=module,
        action=action,
        cost_saved=cost_saved,
        co2_avoided_kg=co2_kg,
        peak_shaved_kw=peak_kw,
        region_code=region_code,
        details_json=details
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_summary(db: Session):
    entries = db.query(LedgerEntryDB).all()
    total_cost = sum(e.cost_saved for e in entries)
    total_co2 = sum(e.co2_avoided_kg for e in entries)
    total_peak = sum(e.peak_shaved_kw for e in entries)
    by_module = {}
    by_region = {}
    for e in entries:
        by_module[e.module] = by_module.get(e.module, 0) + e.cost_saved
        by_region[e.region_code] = by_region.get(e.region_code, 0) + e.cost_saved
    return {
        "total_cost_saved": total_cost,
        "total_co2_avoided_kg": total_co2,
        "total_peak_shaved_kw": total_peak,
        "total_entries": len(entries),
        "by_module": by_module,
        "by_region": by_region
    }

def list_entries(db: Session, limit=100):
    return db.query(LedgerEntryDB).order_by(LedgerEntryDB.timestamp.desc()).limit(limit).all()
