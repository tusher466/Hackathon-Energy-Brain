import numpy as np
import cv2
from typing import List, Dict, Tuple
import base64
import io
from PIL import Image

def analyze_thermal_image(image_array: np.ndarray, region_code: str = "BD") -> Dict:
    """
    image_array: HxWx3 or HxW thermal visualization (temperature encoded as pixel)
    We assume input is already temperature map or color thermal.
    We'll detect hot regions.
    """
    # Convert to grayscale temperature estimate if color
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array

    # Normalize
    norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Threshold hot
    # Hot = > 200 in normalized, but adaptive
    _, thresh_hot = cv2.threshold(norm, 200, 255, cv2.THRESH_BINARY)
    _, thresh_warm = cv2.threshold(norm, 160, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh_hot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    defects = []
    annotated = image_array.copy()
    if len(annotated.shape) == 2:
        annotated = cv2.cvtColor(annotated, cv2.COLOR_GRAY2BGR)

    from app.data.regions import get_region
    region = get_region(region_code)

    total_loss_pct = 0.0
    idx = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 20 or area > 5000:
            continue
        x,y,w,h = cv2.boundingRect(cnt)
        # Estimate temp delta: brighter => hotter
        roi = gray[y:y+h, x:x+w]
        mean_temp = float(np.mean(roi))
        # background mean
        bg_mean = float(np.mean(gray))
        delta = mean_temp - bg_mean
        # Classify by shape
        aspect = w/float(h+1e-6)
        if area < 100 and delta > 20:
            dtype = "hotspot_cell"
            severity = "high" if delta>30 else "medium"
            eff_loss = 2.5
        elif aspect > 3 and delta > 10:
            dtype = "bypass_diode"
            severity = "high"
            eff_loss = 5.0
        elif area > 500 and delta < 10:
            dtype = "soiling"
            severity = "low"
            eff_loss = 1.0
        else:
            dtype = "string_fault"
            severity = "medium"
            eff_loss = 3.0

        yearly_kwh = eff_loss/100 * 1.5 * 365  # assume 1.5kWh per day per panel baseline ~550
        # money loss per region
        price = region.price_per_kwh_day if hasattr(region, 'price_per_kwh_day') else 0.15
        money_loss = yearly_kwh * price

        defects.append({
            "id": f"D{idx}",
            "type": dtype,
            "severity": severity,
            "bbox": [int(x), int(y), int(x+w), int(y+h)],
            "temp_delta_c": float(delta),
            "efficiency_loss_pct": float(eff_loss),
            "yearly_loss_kwh": float(yearly_kwh),
            "money_loss": float(money_loss),
            "recommendation": {
                "hotspot_cell": "Replace cell, check soldering, schedule inspection within 7 days",
                "bypass_diode": "Check diode box, replace diode, immediate priority",
                "soiling": "Clean panels, check for bird droppings/dust",
                "string_fault": "Check string wiring and inverter MPPT"
            }[dtype]
        })
        # Draw
        color = (0,0,255) if severity=="high" else (0,255,255) if severity=="medium" else (0,255,0)
        cv2.rectangle(annotated, (x,y), (x+w, y+h), color, 2)
        cv2.putText(annotated, f"{dtype[:3]}:{severity}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        total_loss_pct += eff_loss
        idx+=1

    # Encode annotated image to base64
    _, buffer = cv2.imencode('.jpg', annotated)
    b64 = base64.b64encode(buffer).decode('utf-8')

    total_yearly = sum(d['yearly_loss_kwh'] for d in defects)
    total_money = sum(d['money_loss'] for d in defects)
    summary = f"Detected {len(defects)} defects, total efficiency loss {total_loss_pct:.1f}%, yearly {total_yearly:.0f} kWh, money loss {region.currency_symbol}{total_money:.1f}"

    return {
        "defects": defects,
        "annotated_image_b64": b64,
        "total_efficiency_loss_pct": total_loss_pct,
        "total_yearly_loss_kwh": total_yearly,
        "total_money_loss": total_money,
        "summary": summary
    }

def generate_synthetic_thermal_sample(seed=0, region_code="BD"):
    from app.data.synthetic import generate_thermal_image
    temp_map, color_map, raw_defects = generate_thermal_image(seed=seed)
    result = analyze_thermal_image(color_map, region_code=region_code)
    return result, color_map
