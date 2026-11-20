from app.schemas.common import RegionProfile

REGION_PROFILES = {
    "BD": RegionProfile(
        code="BD",
        name="Bangladesh - Dhaka",
        currency="BDT",
        currency_symbol="৳",
        tariff_structure="Time-of-use with evening peak 18-23",
        peak_hours=[18,19,20,21,22,23],
        carbon_factor_avg_kg_per_kwh=0.68,
        carbon_factor_marginal_kg_per_kwh=0.82,
        price_per_kwh_day=8.5,
        price_per_kwh_night=6.2,
        price_per_kwh_peak=12.8,
        voltage_level="11kV/0.4kV",
        description="High grid carbon, evening peak driven by residential+commercial, high aircon sensitivity."
    ),
    "DE": RegionProfile(
        code="DE",
        name="Germany - Berlin",
        currency="EUR",
        currency_symbol="€",
        tariff_structure="Day-ahead market + peak/offpeak",
        peak_hours=[8,9,10,17,18,19],
        carbon_factor_avg_kg_per_kwh=0.38,
        carbon_factor_marginal_kg_per_kwh=0.55,
        price_per_kwh_day=0.32,
        price_per_kwh_night=0.24,
        price_per_kwh_peak=0.42,
        voltage_level="20kV/0.4kV",
        description="Day-ahead pricing, lower carbon factor due to renewables, morning+evening peaks."
    ),
    "US": RegionProfile(
        code="US",
        name="USA - PJM Region",
        currency="USD",
        currency_symbol="$",
        tariff_structure="LMP nodal pricing",
        peak_hours=[14,15,16,17,18,19],
        carbon_factor_avg_kg_per_kwh=0.45,
        carbon_factor_marginal_kg_per_kwh=0.65,
        price_per_kwh_day=0.15,
        price_per_kwh_night=0.08,
        price_per_kwh_peak=0.28,
        voltage_level="13.8kV/0.48kV",
        description="LMP-based, afternoon peak summer driven, moderate carbon, high price volatility."
    ),
}

def get_region(code: str) -> RegionProfile:
    return REGION_PROFILES.get(code.upper(), REGION_PROFILES["BD"])

def list_regions():
    return list(REGION_PROFILES.values())
