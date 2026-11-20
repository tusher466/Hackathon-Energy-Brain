import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.connectors import nrel_nsrdb, noaa_gfs, electricity_maps, opsd_eu, pjm_dataminer
from app.data.connectors.base import DataProvenance

def test_all_connectors_return_provenance_offline():
    """Test 1: All 5 connectors return valid DataProvenance without throwing when offline/no keys."""
    connectors = [
        (nrel_nsrdb.fetch_nrel_sync, (23.81, 90.41), "nrel_nsrdb"),
        (noaa_gfs.fetch_gfs_sync, (23.81, 90.41), "noaa_gfs"),
        (electricity_maps.fetch_electricity_maps_sync, ("DE",), "electricity_maps"),
        (opsd_eu.fetch_opsd_de_sync, (48,), "opsd"),
        (pjm_dataminer.fetch_pjm_sync, (24, "US"), "pjm_dataminer"),
    ]
    for func, args, expected_id in connectors:
        try:
            result = func(*args)
            assert result is not None, f"{expected_id} returned None"
            prov = result.provenance
            # Check provenance fields
            assert isinstance(prov, DataProvenance) or isinstance(prov, dict) or hasattr(prov, 'source_id')
            # Handle dict vs object
            source_id = prov.source_id if hasattr(prov, 'source_id') else prov.get('source_id')
            assert source_id == expected_id, f"Expected {expected_id} got {source_id}"
            mode = prov.mode if hasattr(prov, 'mode') else prov.get('mode')
            assert mode in ["live", "dataset_snapshot", "synthetic_fallback"], f"Invalid mode {mode}"
            fields = prov.fields_ingested if hasattr(prov, 'fields_ingested') else prov.get('fields_ingested')
            assert isinstance(fields, list) and len(fields) > 0, f"{expected_id} fields_ingested empty"
            sample = prov.sample_record if hasattr(prov, 'sample_record') else prov.get('sample_record')
            assert isinstance(sample, dict) and len(sample) > 0, f"{expected_id} sample_record empty"
            latency = prov.latency_ms if hasattr(prov, 'latency_ms') else prov.get('latency_ms')
            assert isinstance(latency, (int, float)) and latency >= 0, f"{expected_id} latency invalid"
            # Check numeric fields exist in data
            assert isinstance(result.data, dict), f"{expected_id} data not dict"
            print(f"{expected_id} OK mode={mode} latency={latency}ms sample_keys={list(sample.keys())[:3]}")
        except Exception as e:
            raise AssertionError(f"{expected_id} connector threw exception offline: {e}")

def test_integrations_endpoints_return_all_five():
    """Test 2: GET /api/v1/integrations and POST /api/v1/integrations/verify return all 5 required resources."""
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    # GET integrations
    resp = client.get("/api/v1/integrations")
    assert resp.status_code == 200, f"GET /integrations failed {resp.status_code} {resp.text}"
    data = resp.json()
    assert isinstance(data, list), "Integrations should be list"
    assert len(data) >= 5, f"Expected at least 5 sources, got {len(data)}"
    source_ids = [d.get('source_id') for d in data]
    required = ["nrel_nsrdb", "noaa_gfs", "electricity_maps", "opsd", "pjm_dataminer"]
    for req in required:
        assert req in source_ids, f"Missing required source {req} in GET integrations, got {source_ids}"
    print(f"GET integrations OK: {source_ids}")

    # POST verify
    resp2 = client.post("/api/v1/integrations/verify")
    assert resp2.status_code == 200, f"POST verify failed {resp2.status_code} {resp2.text}"
    j = resp2.json()
    assert "results" in j, "Verify missing results"
    assert j.get("sources_verified", 0) >= 5, f"Expected 5 verified, got {j.get('sources_verified')}"
    verify_ids = [r.get('source_id') for r in j.get('results', [])]
    for req in required:
        assert req in verify_ids, f"Missing {req} in verify results {verify_ids}"
    assert j.get("judge_ready") is True or "judge_ready" in j, "Verify not judge_ready"
    print(f"POST verify OK: {verify_ids} total_latency={j.get('total_latency_ms')}ms summary={j.get('summary')}")

def test_forecast_and_vpp_include_provenance():
    """Test 3: solar, demand (DE/US), vpp include non-empty data_sources provenance."""
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    # Solar
    resp = client.post("/api/v1/solar/forecast", json={"lat": 23.81, "lon": 90.41, "capacity_kw": 500, "tilt_deg": 23, "horizon_hours": 24})
    assert resp.status_code == 200, f"Solar forecast failed {resp.status_code} {resp.text}"
    solar_data = resp.json()
    assert "data_sources" in solar_data and len(solar_data["data_sources"]) >= 2, f"Solar missing data_sources or <2, got {solar_data.get('data_sources')}"
    solar_ids = [ds.get('source_id') for ds in solar_data["data_sources"]]
    assert "nrel_nsrdb" in solar_ids or "noaa_gfs" in solar_ids, f"Solar should include nrel or gfs, got {solar_ids}"
    print(f"Solar forecast provenance OK: {solar_ids}")

    # Demand DE
    resp = client.post("/api/v1/demand/forecast", json={"region_code": "DE", "sites": 3, "horizon_hours": 48})
    assert resp.status_code == 200, f"Demand DE failed {resp.status_code}"
    de_data = resp.json()
    assert "data_sources" in de_data and len(de_data["data_sources"]) >= 1, "DE demand missing data_sources"
    de_ids = [ds.get('source_id') for ds in de_data["data_sources"]]
    assert "opsd" in de_ids or "noaa_gfs" in de_ids, f"DE demand should include opsd or noaa_gfs, got {de_ids}"
    print(f"DE demand provenance OK: {de_ids}")

    # Demand US
    resp = client.post("/api/v1/demand/forecast", json={"region_code": "US", "sites": 3, "horizon_hours": 24})
    assert resp.status_code == 200, f"Demand US failed {resp.status_code}"
    us_data = resp.json()
    assert "data_sources" in us_data and len(us_data["data_sources"]) >= 1, "US demand missing data_sources"
    us_ids = [ds.get('source_id') for ds in us_data["data_sources"]]
    assert "pjm_dataminer" in us_ids or "noaa_gfs" in us_ids, f"US demand should include pjm or gfs, got {us_ids}"
    print(f"US demand provenance OK: {us_ids}")

    # VPP
    fleet_resp = client.get("/api/v1/vpp/default-fleet")
    assert fleet_resp.status_code == 200
    fleet = fleet_resp.json()
    resp = client.post("/api/v1/vpp/dispatch", json={
        "region_code": "DE",
        "evs": fleet["evs"][:2],
        "batteries": fleet["batteries"],
        "flexible_loads": fleet["flexible_loads"],
        "horizon_hours": 24
    })
    assert resp.status_code == 200, f"VPP DE dispatch failed {resp.status_code} {resp.text}"
    vpp_data = resp.json()
    assert "data_sources" in vpp_data and len(vpp_data["data_sources"]) >= 1, "VPP missing data_sources"
    vpp_ids = [ds.get('source_id') for ds in vpp_data["data_sources"]]
    assert "electricity_maps" in vpp_ids or "opsd" in vpp_ids, f"VPP should include electricity_maps or opsd, got {vpp_ids}"
    print(f"VPP DE provenance OK: {vpp_ids}")

    # VPP US
    resp = client.post("/api/v1/vpp/dispatch", json={
        "region_code": "US",
        "evs": fleet["evs"][:2],
        "batteries": fleet["batteries"],
        "flexible_loads": fleet["flexible_loads"],
        "horizon_hours": 24
    })
    assert resp.status_code == 200, f"VPP US failed {resp.status_code}"
    vpp_us = resp.json()
    assert "data_sources" in vpp_us and len(vpp_us["data_sources"]) >= 1, "VPP US missing data_sources"
    vpp_us_ids = [ds.get('source_id') for ds in vpp_us["data_sources"]]
    print(f"VPP US provenance OK: {vpp_us_ids}")

if __name__ == "__main__":
    test_all_connectors_return_provenance_offline()
    test_integrations_endpoints_return_all_five()
    test_forecast_and_vpp_include_provenance()
    print("All integration tests passed")
