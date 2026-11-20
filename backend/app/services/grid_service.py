import random
from typing import List, Dict
from datetime import datetime, timedelta

SCENARIOS = {
    "cloud_collapse": {
        "description": "Sudden cloud collapse + PV ramp down",
        "events": [
            {"type": "renewable_failure", "hour": 2, "severity": "high", "description": "PV generation drops 80% due to dense cloud mass"},
            {"type": "frequency_dip", "hour": 2, "severity": "medium", "description": "Grid frequency drops to 49.2 Hz"},
            {"type": "load_shedding", "hour": 3, "severity": "medium", "description": "Non-critical loads shed 15MW"},
        ]
    },
    "wind_lull": {
        "description": "Prolonged wind lull across region",
        "events": [
            {"type": "wind_failure", "hour": 1, "severity": "high", "description": "Wind generation 90% below forecast for 6h"},
            {"type": "price_spike", "hour": 2, "severity": "high", "description": "Day-ahead price spikes 3x"},
        ]
    },
    "line_trip": {
        "description": "Transmission line trip L1",
        "events": [
            {"type": "line_trip", "hour": 0, "severity": "critical", "description": "220kV line L1 trips, islanding suburb A"},
            {"type": "islanding", "hour": 0, "severity": "high", "description": "Substation S1 islands, 30MW isolated"},
        ]
    },
    "cyber_outage": {
        "description": "SCADA communication loss",
        "events": [
            {"type": "cyber", "hour": 0, "severity": "critical", "description": "RTU communication loss, 40% observability lost"},
            {"type": "manual_override", "hour": 1, "severity": "medium", "description": "Switch to manual dispatch"},
        ]
    }
}

def generate_blackstart_plan(scenario: str, region_code: str):
    base_nodes = ["G1-Hydro", "G2-Gas", "S1-Sub", "S2-Sub", "S3-Sub", "L1-Indust", "L2-Commercial", "L3-Residential", "Batt-1", "EV-Fleet"]
    # recovery sequence deterministic but with region variation
    steps = []
    energized = []
    # cranking power
    steps.append({
        "step_id": 1,
        "action": "Start cranking source G1-Hydro (black start capable)",
        "energized_nodes": ["G1-Hydro"],
        "frequency_hz": 50.0,
        "voltage_pu": 0.95,
        "load_mw": 0.0,
        "timestamp": "00:05",
        "status": "completed"
    })
    energized = ["G1-Hydro"]
    steps.append({
        "step_id": 2,
        "action": "Energize bus S1-Sub and Batt-1 for voltage support",
        "energized_nodes": ["G1-Hydro", "S1-Sub", "Batt-1"],
        "frequency_hz": 49.9,
        "voltage_pu": 0.97,
        "load_mw": 0.5,
        "timestamp": "00:12",
        "status": "completed"
    })
    energized = ["G1-Hydro", "S1-Sub", "Batt-1"]
    steps.append({
        "step_id": 3,
        "action": "Crank G2-Gas from Hydro",
        "energized_nodes": ["G1-Hydro", "G2-Gas", "S1-Sub", "Batt-1"],
        "frequency_hz": 50.0,
        "voltage_pu": 1.0,
        "load_mw": 1.2,
        "timestamp": "00:28",
        "status": "completed"
    })
    steps.append({
        "step_id": 4,
        "action": "Pickup critical industrial load L1-Indust (5MW)",
        "energized_nodes": ["G1-Hydro", "G2-Gas", "S1-Sub", "S2-Sub", "L1-Indust", "Batt-1"],
        "frequency_hz": 49.8,
        "voltage_pu": 0.98,
        "load_mw": 5.0,
        "timestamp": "00:45",
        "status": "completed"
    })
    steps.append({
        "step_id": 5,
        "action": "Synchronize and pickup L2-Commercial and EV fleet charging (delayed)",
        "energized_nodes": ["G1-Hydro","G2-Gas","S1-Sub","S2-Sub","S3-Sub","L1-Indust","L2-Commercial","Batt-1","EV-Fleet"],
        "frequency_hz": 49.9,
        "voltage_pu": 0.99,
        "load_mw": 18.0,
        "timestamp": "01:15",
        "status": "completed"
    })
    steps.append({
        "step_id": 6,
        "action": "Restore L3-Residential, full system restored",
        "energized_nodes": base_nodes,
        "frequency_hz": 50.0,
        "voltage_pu": 1.0,
        "load_mw": 28.0,
        "timestamp": "01:50",
        "status": "completed"
    })
    # network graph
    graph = {
        "nodes": [{"id": n, "type": "gen" if n.startswith("G") else "load" if n.startswith("L") else "sub" if n.startswith("S") else "storage"} for n in base_nodes],
        "edges": [
            {"from": "G1-Hydro", "to": "S1-Sub"},
            {"from": "G2-Gas", "to": "S1-Sub"},
            {"from": "S1-Sub", "to": "S2-Sub"},
            {"from": "S2-Sub", "to": "S3-Sub"},
            {"from": "S2-Sub", "to": "L1-Indust"},
            {"from": "S3-Sub", "to": "L2-Commercial"},
            {"from": "S3-Sub", "to": "L3-Residential"},
            {"from": "Batt-1", "to": "S1-Sub"},
            {"from": "EV-Fleet", "to": "S3-Sub"},
        ]
    }
    events = SCENARIOS.get(scenario, SCENARIOS["cloud_collapse"])["events"]
    return {
        "events": events,
        "recovery_plan": steps,
        "network_graph": graph,
        "estimated_recovery_minutes": 110
    }

# Simple RAG knowledge base search
import os
from pathlib import Path

def load_knowledge_docs():
    kb_path = Path(__file__).parent.parent / "knowledge"
    docs = []
    if kb_path.exists():
        for md in kb_path.glob("*.md"):
            try:
                text = md.read_text(encoding="utf-8")
                docs.append({"file": md.name, "content": text})
            except:
                pass
    if not docs:
        # fallback hardcoded
        docs = [
            {"file": "black_start_procedure.md", "content": "Black start procedure: Step 1 cranking source hydro, Step 2 energize busses, Step 3 crank thermal units, Step 4 pickup critical loads 5-10% increments, maintain frequency 49.5-50.5Hz, voltage 0.95-1.05pu. Use battery for voltage support."},
            {"file": "frequency_control.md", "content": "Frequency control: If frequency drops below 49.5Hz, shed 10% non-critical loads. If below 49.0Hz, shed 25%. Restore in 5MW blocks."},
            {"file": "ev_fleet_guideline.md", "content": "EV fleet: During black start, defer EV charging until stable frequency. Use V2G if available to support grid."}
        ]
    return docs

def simple_tfidf_search(query: str, docs: List[Dict], top_k=2):
    # Very simple keyword overlap
    q_words = set(query.lower().split())
    scored = []
    for d in docs:
        content_low = d['content'].lower()
        overlap = len(q_words & set(content_low.split()))
        scored.append((overlap, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:top_k]]

def generate_rule_based_answer(question: str, scenario: str, docs: List[Dict], recovery_plan: List[Dict]):
    # Provide grounded answer
    q = question.lower()
    relevant = simple_tfidf_search(question, docs, top_k=2)
    citations = [r['file'] for r in relevant]
    steps_ref = []
    answer_parts = []
    if "black start" in q or "recover" in q:
        answer_parts.append(f"For scenario {scenario}, recovery follows 6 steps. Current plan starts with hydro cranking at 00:05, energizes S1 substation with battery support, then cranks gas unit. Critical industrial load is picked up at step 4 (00:45, 5MW).")
        steps_ref = [1,2,4]
    if "frequency" in q:
        answer_parts.append("Frequency must stay 49.5-50.5Hz. If below 49.5Hz, shed 10% non-critical; below 49.0Hz shed 25%. Recovery plan maintains 49.8-50.0Hz as per steps 4-6.")
        steps_ref.append(4)
    if "ev" in q:
        answer_parts.append("EV fleet charging is deferred until step 5 (01:15) after stable frequency achieved. Optionally V2G can provide 2-3MW support if SoC >60%.")
        steps_ref.append(5)
    if "battery" in q:
        answer_parts.append("Battery Batt-1 provides voltage support from step 2, helps with black start voltage regulation 0.97-1.0pu.")
        steps_ref.extend([2,3])
    if not answer_parts:
        # generic
        answer_parts.append(f"Scenario {scenario}: {relevant[0]['content'][:300]} Recovery timeline about 110 minutes, 6 steps. Last step restores residential load L3 at 01:50.")
        steps_ref = [1,6]

    answer = " ".join(answer_parts)
    answer += f" (Sources: {', '.join(citations)})"
    return answer, citations, list(set(steps_ref))
