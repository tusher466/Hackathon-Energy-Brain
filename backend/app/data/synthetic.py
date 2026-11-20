import numpy as np
import math
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _rng(seed=None):
    if seed is None:
        return np.random.default_rng()
    return np.random.default_rng(seed)

def clear_sky_irradiance(hour: float, lat: float, day_of_year: int, tilt_deg: float, capacity_kw: float) -> float:
    """Simple clear-sky model: solar geometry * capacity."""
    # Declination angle
    decl = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
    # Hour angle
    hour_angle = 15 * (hour - 12)
    lat_r = math.radians(lat)
    decl_r = math.radians(decl)
    hour_r = math.radians(hour_angle)
    # cos zenith
    cos_zenith = math.sin(lat_r) * math.sin(decl_r) + math.cos(lat_r) * math.cos(decl_r) * math.cos(hour_r)
    cos_zenith = max(0, cos_zenith)
    # air mass approx
    # irradiance = 1000 * cos_zenith * tilt factor
    tilt_r = math.radians(tilt_deg)
    # simple tilt correction: increase when sun near tilt optimum
    tilt_factor = max(0.5, math.cos(tilt_r) * cos_zenith + math.sin(tilt_r) * math.sqrt(1 - cos_zenith**2) * 0.3 + 0.7)
    irradiance = 1000 * cos_zenith * tilt_factor  # W/m2
    # Convert to power kW: assume standard efficiency scaling with capacity
    # capacity_kw is at 1000 W/m2
    power = capacity_kw * (irradiance / 1000.0)
    # Early morning / late evening clip
    if hour < 5 or hour > 19:
        power *= 0.1
    return float(max(0, power))

def generate_cloud_field(size=32, cloud_cover=0.4, seed=None) -> np.ndarray:
    rng = _rng(seed)
    # Perlin-like noise via filtered uniform
    field = rng.random((size, size))
    # smooth
    from scipy.ndimage import gaussian_filter
    field = gaussian_filter(field, sigma=2.0)
    # threshold to create clouds
    threshold = np.quantile(field, 1 - cloud_cover)
    cloud_transmission = np.where(field > threshold, rng.uniform(0.2, 0.7, size=(size,size)), 1.0)
    # random variation 0.8-1.0 for clear
    cloud_transmission = np.clip(cloud_transmission + rng.normal(0, 0.05, size=(size,size)), 0.1, 1.0)
    return cloud_transmission

def advect_cloud_field(field: np.ndarray, wind_vector: Tuple[float,float], steps: int = 5, seed=None) -> List[np.ndarray]:
    """Advect field by wind vector (vx, vy) in pixels per step."""
    from scipy.ndimage import shift
    rng = _rng(seed)
    frames = []
    current = field.copy()
    for i in range(steps):
        frames.append(current.copy())
        # shift
        current = shift(current, shift=wind_vector, mode='wrap', order=1)
        # add small evolution
        current = np.clip(current + rng.normal(0, 0.02, size=current.shape), 0.1, 1.0)
    return frames

def generate_solar_timeseries(lat, lon, capacity_kw, tilt_deg, horizon_hours, start_dt: datetime = None):
    if start_dt is None:
        start_dt = _utcnow().replace(minute=0, second=0, microsecond=0)
    day_of_year = start_dt.timetuple().tm_yday
    cloud_base = generate_cloud_field(size=32, cloud_cover=0.35, seed=int(abs(lat*10)) % 1000)
    rng = _rng(int(abs(lon*10+lat*10)) % 10000)
    wind_vec = (float(rng.uniform(-1.5, 1.5)), float(rng.uniform(-0.5, 1.5)))
    cloud_frames = advect_cloud_field(cloud_base, wind_vec, steps=min(horizon_hours, 24))
    # Repeat to cover horizon
    extended_frames = []
    for i in range(horizon_hours):
        extended_frames.append(cloud_frames[i % len(cloud_frames)])

    forecast = []
    for h in range(horizon_hours):
        ts = start_dt + timedelta(hours=h)
        hour_float = ts.hour + ts.minute/60.0
        clear_power = clear_sky_irradiance(hour_float, lat, day_of_year, tilt_deg, capacity_kw)
        # sample transmission at center
        size = extended_frames[h].shape[0]
        center = extended_frames[h][size//2 -2:size//2+2, size//2-2:size//2+2].mean()
        p50 = clear_power * center
        # uncertainty increases with horizon
        horizon_factor = 1 + h*0.02
        p10 = p50 * max(0.2, 1 - 0.3*horizon_factor* (1-center))
        p90 = p50 * min(1.4, 1 + 0.2*horizon_factor* (1-center))
        # variability index: std of nearby cloud field
        var_index = float(np.std(extended_frames[h]) * 2.0)
        forecast.append({
            "timestamp": ts,
            "p10": float(max(0, p10)),
            "p50": float(max(0, p50)),
            "p90": float(max(0, p90)),
            "variability_index": var_index,
        })
    return forecast, extended_frames, wind_vec

def generate_demand_timeseries(region_code: str, sites: int, horizon_hours: int, start_dt: datetime = None, seed=None):
    if start_dt is None:
        start_dt = _utcnow().replace(minute=0, second=0, microsecond=0)
    rng = _rng(seed if seed is not None else hash((region_code, sites, horizon_hours)) % (2**32))
    # base patterns per region
    if region_code == "BD":
        base_load = 400  # kW per site
        peak_hours = [18,19,20,21,22]
        temp_sensitivity = 0.08
    elif region_code == "DE":
        base_load = 350
        peak_hours = [8,9,17,18,19]
        temp_sensitivity = 0.04
    else: # US
        base_load = 500
        peak_hours = [14,15,16,17,18]
        temp_sensitivity = 0.1

    forecasts = []
    for h in range(horizon_hours):
        ts = start_dt + timedelta(hours=h)
        weekday = ts.weekday()  # 0 mon
        is_weekend = weekday >=5
        hour = ts.hour
        # weekday pattern
        daily_profile = math.sin(2*math.pi*(hour-6)/24)*0.3 + 0.7
        if is_weekend:
            daily_profile *= 0.8
        # peak boost
        if hour in peak_hours:
            daily_profile *= 1.4
        # temperature effect
        temp = 25 + 10*math.sin(2*math.pi*h/24) + float(rng.normal(0,1))
        temp_effect = 1 + temp_sensitivity * max(0, temp-22)/10

        # economic indicator - slow varying
        economic = 1.0 + 0.1*math.sin(2*math.pi*h/(24*30))

        p50 = base_load * sites * daily_profile * temp_effect * economic
        p50 += float(rng.normal(0, base_load*0.05))
        # quantile spread
        spread = 0.15 + 0.002*h
        p10 = p50 * (1 - spread)
        p90 = p50 * (1 + spread)
        forecasts.append({
            "timestamp": ts,
            "p10": float(max(0, p10)),
            "p50": float(max(0, p50)),
            "p90": float(max(0, p90)),
            "variability_index": float(abs(spread)),
        })
    return forecasts

def generate_price_carbon_forecasts(region_code: str, horizon: int, seed=None):
    # Use region profile
    from app.data.regions import get_region
    reg = get_region(region_code)
    prices = []
    carbons = []
    rng = _rng(seed if seed is not None else hash((region_code, horizon)) % (2**32))
    for h in range(horizon):
        hour = h % 24
        if hour in reg.peak_hours:
            price = reg.price_per_kwh_peak + float(rng.normal(0, reg.price_per_kwh_peak*0.1))
            carbon = reg.carbon_factor_marginal_kg_per_kwh + float(rng.normal(0, 0.05))
        elif 0 <= hour <= 5:
            price = reg.price_per_kwh_night + float(rng.normal(0, reg.price_per_kwh_night*0.05))
            carbon = reg.carbon_factor_avg_kg_per_kwh * 0.9
        else:
            price = reg.price_per_kwh_day + float(rng.normal(0, reg.price_per_kwh_day*0.08))
            carbon = reg.carbon_factor_avg_kg_per_kwh
        prices.append(max(0.01, float(price)))
        carbons.append(max(0.05, float(carbon)))
    return prices, carbons

def generate_thermal_image(seed=None, width=640, height=480):
    """Generate synthetic thermal drone image of PV array."""
    rng = _rng(seed)
    # background
    img = rng.normal(30, 2, (height, width))  # temperature C
    # Draw panels as rectangles
    panel_temps = []
    num_rows = 6
    num_cols = 10
    panel_h = height // (num_rows+2)
    panel_w = width // (num_cols+2)
    defects = []
    for r in range(num_rows):
        for c in range(num_cols):
            y1 = (r+1)*panel_h
            x1 = (c+1)*panel_w
            y2 = y1 + int(panel_h*0.8)
            x2 = x1 + int(panel_w*0.8)
            # base panel temp 45C
            base = 45 + float(rng.normal(0,1))
            img[y1:y2, x1:x2] = base + rng.normal(0,0.5, (y2-y1, x2-x1))
            panel_temps.append((r,c,base,x1,y1,x2,y2))
    # inject defects
    num_defects = int(rng.integers(3,8))
    for i in range(num_defects):
        idx = int(rng.integers(0, len(panel_temps)))
        r,c,base,x1,y1,x2,y2 = panel_temps[idx]
        defect_type = rng.choice(["hotspot_cell", "bypass_diode", "soiling", "string_fault"])
        if defect_type == "hotspot_cell":
            # small hot region
            cx = int(rng.integers(x1+5, max(x1+6, x2-5)))
            cy = int(rng.integers(y1+5, max(y1+6, y2-5)))
            img[max(0,cy-5):cy+5, max(0,cx-5):cx+5] += float(rng.uniform(15,35))
            temp_delta = 20.0
        elif defect_type == "bypass_diode":
            # hot stripe across panel
            img[y1:y1+5, x1:x2] += float(rng.uniform(10,20))
            temp_delta = 15.0
        elif defect_type == "soiling":
            img[y1:y2, x1:x2] -= float(rng.uniform(3,6))
            temp_delta = -4.0
        else: # string_fault
            img[y1:y2, x1:x2] += float(rng.uniform(5,10))
            temp_delta = 8.0
        defects.append({
            "panel_row": r,
            "panel_col": c,
            "type": defect_type,
            "bbox": [x1,y1,x2,y2],
            "temp_delta": temp_delta,
        })
    # Normalize to 0-255 for visualization
    img_norm = ((img - img.min())/(img.max()-img.min())*255).astype(np.uint8)
    # Apply colormap via OpenCV if available else return grayscale
    try:
        import cv2
        img_color = cv2.applyColorMap(img_norm, cv2.COLORMAP_JET)
    except:
        img_color = np.stack([img_norm]*3, axis=-1)
    return img, img_color, defects
