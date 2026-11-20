import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.data.synthetic import generate_solar_timeseries
from app.ml.cloud_motion import estimate_motion
import numpy as np

def test_solar_forecast_monotonic():
    fc, frames, vec = generate_solar_timeseries(23.8, 90.4, 500, 23, 24)
    for p in fc:
        assert p["p10"] <= p["p50"] <= p["p90"], f"Non monotonic {p}"
        assert p["p50"] >= 0
    print("solar monotonic ok")

def test_cloud_motion_error_under_tolerance():
    # Create synthetic shifted frames
    field = np.random.rand(32,32)
    from scipy.ndimage import shift
    true_vec = (2.0, -1.0)  # vx, vy but shift expects vy,vx
    shifted = shift(field, shift=(true_vec[1], true_vec[0]), mode='wrap', order=1)
    est = estimate_motion(field, shifted)
    # est should be close to true_vec
    err = np.sqrt((est[0]-true_vec[0])**2 + (est[1]-true_vec[1])**2)
    print(f"true {true_vec}, est {est}, err {err}")
    assert err < 2.0, f"Motion error too high {err}"

if __name__ == "__main__":
    test_solar_forecast_monotonic()
    test_cloud_motion_error_under_tolerance()
