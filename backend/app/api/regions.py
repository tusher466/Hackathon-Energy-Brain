from fastapi import APIRouter
from app.data.regions import list_regions, get_region, REGION_PROFILES

router = APIRouter(prefix="/regions", tags=["regions"])

@router.get("")
def get_regions():
    return list_regions()

@router.get("/{code}")
def get_one_region(code: str):
    return get_region(code)

@router.get("/{code}/tariff")
def get_tariff(code: str):
    reg = get_region(code)
    # hourly tariff for 24h
    tariff = []
    for h in range(24):
        if h in reg.peak_hours:
            price = reg.price_per_kwh_peak
        elif 0 <= h <= 5:
            price = reg.price_per_kwh_night
        else:
            price = reg.price_per_kwh_day
        tariff.append(price)
    return {"region": reg, "hourly_tariff": tariff}
