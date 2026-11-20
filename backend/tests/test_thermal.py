import sys
sys.path.insert(0, "E:/Project/backend")
from app.ml.thermal import generate_synthetic_thermal_sample

def test_thermal():
    result, img = generate_synthetic_thermal_sample(seed=42, region_code="BD")
    print(result["summary"])
    assert result["total_efficiency_loss_pct"] >= 0
    assert len(result["defects"]) >= 1
    assert result["annotated_image_b64"] is not None
    print("thermal ok")

if __name__ == "__main__":
    test_thermal()
