from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.ledger_service import LedgerEntryDB, ApprovalDB, get_summary, list_entries
from app.schemas.common import LedgerSummary, LedgerEntry, ApprovalItem
from datetime import datetime, timezone
import uuid

def _now():
    return datetime.now(timezone.utc)

router = APIRouter(prefix="/ledger", tags=["ledger"])

@router.get("/summary", response_model=LedgerSummary)
def ledger_summary(db: Session = Depends(get_db)):
    s = get_summary(db)
    # determine currency from most common region
    from app.data.regions import get_region
    # default BDT
    currency = "BDT"
    if s["by_region"]:
        top_region = max(s["by_region"], key=lambda k: s["by_region"][k])
        reg = get_region(top_region)
        currency = reg.currency
    return LedgerSummary(
        total_cost_saved=s["total_cost_saved"],
        total_co2_avoided_kg=s["total_co2_avoided_kg"],
        total_peak_shaved_kw=s["total_peak_shaved_kw"],
        total_entries=s["total_entries"],
        by_module=s["by_module"],
        by_region=s["by_region"],
        currency=currency
    )

@router.get("/entries")
def get_entries(db: Session = Depends(get_db), limit: int = 50):
    entries = list_entries(db, limit=limit)
    result = []
    for e in entries:
        result.append({
            "id": e.id,
            "timestamp": e.timestamp,
            "module": e.module,
            "action": e.action,
            "cost_saved": e.cost_saved,
            "co2_avoided_kg": e.co2_avoided_kg,
            "peak_shaved_kw": e.peak_shaved_kw,
            "region_code": e.region_code,
            "details": e.details_json
        })
    return result

@router.get("/approvals")
def get_approvals(db: Session = Depends(get_db)):
    approvals = db.query(ApprovalDB).order_by(ApprovalDB.timestamp.desc()).limit(20).all()
    if not approvals:
        # seed demo approvals
        demo = [
            {"id": "APPROVAL-1", "action": "Charge 42 EVs 01:00-04:30", "module": "vpp", "description": "Shift EV charging to night low price", "status": "pending", "kpi": {"cost_saved": 118, "co2_saved": 45}},
            {"id": "APPROVAL-2", "action": "Black start step 4 - L1 pickup", "module": "grid", "description": "Pickup 5MW industrial load", "status": "pending", "kpi": {"load": 5}},
        ]
        for d in demo:
            a = ApprovalDB(
                id=d["id"],
                action=d["action"],
                module=d["module"],
                description=d["description"],
                status=d["status"],
                kpi_impact_json=d["kpi"]
            )
            db.add(a)
        db.commit()
        approvals = db.query(ApprovalDB).order_by(ApprovalDB.timestamp.desc()).limit(20).all()

    result = []
    for a in approvals:
        result.append({
            "id": a.id,
            "timestamp": a.timestamp,
            "action": a.action,
            "module": a.module,
            "description": a.description,
            "status": a.status,
            "kpi_impact": a.kpi_impact_json
        })
    return result

@router.post("/approvals/{approval_id}/{decision}")
def decide_approval(approval_id: str, decision: str, db: Session = Depends(get_db)):
    # decision: approve, reject
    entry = db.query(ApprovalDB).filter(ApprovalDB.id == approval_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="approval not found")
    if decision not in ["approve","reject"]:
        raise HTTPException(status_code=400, detail="invalid decision use approve/reject")
    entry.status = "approved" if decision=="approve" else "rejected"
    db.commit()
    return {"id": entry.id, "status": entry.status}

@router.post("/reset")
def reset_ledger(db: Session = Depends(get_db)):
    db.query(LedgerEntryDB).delete()
    db.query(ApprovalDB).delete()
    db.commit()
    return {"status": "reset"}

@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db), format: str = "json"):
    """
    Export ledger as JSON containing csv string (default for frontend compatibility)
    and also supports ?format=csv for direct text/csv download (market-ready).
    """
    entries = list_entries(db, limit=1000)
    lines = ["id,timestamp,module,action,cost_saved,co2_avoided_kg,peak_shaved_kw,region_code"]
    for e in entries:
        # escape commas in action by quoting
        action_escaped = str(e.action).replace(',', ';')
        lines.append(f"{e.id},{e.timestamp},{e.module},{action_escaped},{e.cost_saved},{e.co2_avoided_kg},{e.peak_shaved_kw},{e.region_code}")
    csv_text = "\n".join(lines)
    if format == "csv":
        return PlainTextResponse(csv_text, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=ledger.csv"})
    return {"csv": csv_text}
