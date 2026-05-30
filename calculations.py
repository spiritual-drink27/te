"""
calculations.py – Pure emission-factor math. No I/O, no Streamlit.

Responsibilities:
  - Emission factor constants
  - calculate_emissions() function
  - Emission equivalents (coal, cigarettes, etc.)
  - Environmental title / gamification logic
"""

from dataclasses import dataclass

# ─────────────────────────────────────────────
#  Emission Factors
# ─────────────────────────────────────────────

# kg CO₂ per hour (based on device wattage × grid factor)
PC_FACTORS: dict[str, float] = {
    "Laptop":              0.044,   # ~60 W
    "Desktop":             0.051,   # ~70 W
    "Desktop + Monitor":   0.087,   # ~120 W
    "Laptop + Monitor":    0.065,   # ~90 W
}

# kW of power draw per AC tonnage
AC_POWER_KW: dict[str, float] = {
    "No AC":   0.0,
    "1.0 Ton": 0.9,
    "1.5 Ton": 1.3,
    "2.0 Ton": 1.8,
}

# Indian eastern-region grid: kg CO₂ per kWh
GRID_FACTOR = 0.727

# kg CO₂e per meal
MEAL_FACTORS: dict[str, float] = {
    "Vegetarian":     0.65,
    "Non-Vegetarian": 2.00,
}

# kg CO₂ per page (electricity only)
PRINTER_ELEC: dict[str, float] = {
    "None":          0.0,
    "Inkjet":        0.0005,
    "Laser":         0.0015,
    "Office Copier": 0.0020,
}

PAPER_PER_PAGE = 0.0125   # kg CO₂ per A4 sheet (pulp + process)

# kg CO₂ per km
COMMUTE_FACTORS: dict[str, float] = {
    "Walking":    0.0,
    "Bicycle":    0.0,
    "Two-Wheeler": 0.05163,
    "Bus":        0.015161,
    "CNG Car":    0.10768,
}

# kg CO₂ per litre of fuel
FUEL_EMISSION: dict[str, float] = {
    "Petrol": 2.31,
    "Diesel": 2.68,
}

CAR_MODES = {"Car", "Carpool", "Private Car(DIESEL)", "Private Car(PETROL)"}

# ─────────────────────────────────────────────
#  Emission calculation
# ─────────────────────────────────────────────

@dataclass
class EmissionResult:
    commute:        float
    official_visit: float
    pc:             float
    ac:             float
    meal:           float
    printer:        float
    total:          float

    def as_dict(self) -> dict[str, float]:
        return {
            "commute":        self.commute,
            "official_visit": self.official_visit,
            "pc":             self.pc,
            "ac":             self.ac,
            "meal":           self.meal,
            "printer":        self.printer,
            "total":          self.total,
        }


def _vehicle_emission(fuel_type: str, distance_km: float,
                      mileage_kmpl: float, persons: int) -> float:
    """kg CO₂ for a car/carpool trip."""
    if mileage_kmpl <= 0 or persons <= 0:
        return 0.0
    litres = distance_km / mileage_kmpl
    return FUEL_EMISSION.get(fuel_type, 2.31) * litres / persons


def calculate_emissions(
    transport_mode: str,
    commute_distance: float,
    fuel_type: str,
    mileage: float,
    persons_in_car: int,
    official_visit_km: float,
    pc_type: str,
    pc_hours: float,
    ac_tonnage: str,
    ac_hours: float,
    meal_type: str,
    printer_type: str,
    pages_printed: int,
) -> EmissionResult:

    is_car = transport_mode in CAR_MODES

    # 1. Commute (round-trip)
    if is_car:
        commute = _vehicle_emission(fuel_type, commute_distance * 2,
                                    mileage, persons_in_car)
    else:
        commute = COMMUTE_FACTORS.get(transport_mode, 0.0) * commute_distance * 2

    # 2. Official visit (one-way distance provided)
    if is_car and official_visit_km > 0:
        official_visit = _vehicle_emission(fuel_type, official_visit_km,
                                           mileage, persons_in_car)
    else:
        official_visit = COMMUTE_FACTORS.get(transport_mode, 0.0) * official_visit_km

    # 3. PC
    pc = PC_FACTORS.get(pc_type, 0.0) * pc_hours

    # 4. AC
    ac = AC_POWER_KW.get(ac_tonnage, 0.0) * ac_hours * GRID_FACTOR

    # 5. Meal
    meal = MEAL_FACTORS.get(meal_type, 0.65)

    # 6. Printer
    printer = pages_printed * (PAPER_PER_PAGE + PRINTER_ELEC.get(printer_type, 0.0))

    total = commute + official_visit + pc + ac + meal + printer

    return EmissionResult(commute, official_visit, pc, ac, meal, printer, total)


# ─────────────────────────────────────────────
#  Emission Equivalents
# ─────────────────────────────────────────────

def emission_equivalents(kg_co2: float) -> dict[str, float]:
    """Convert kg CO₂e to relatable real-world equivalents."""
    return {
        "coal_g":        round(kg_co2 / 0.00232, 1),   # grams of coal
        "cigarettes":    round(kg_co2 / 0.014,   1),   # cigarettes smoked
        "phone_charges": round(kg_co2 / 0.008,   1),   # smartphone charges
        "led_hours":     round(kg_co2 / 0.00727, 1),   # LED bulb hours
        "petrol_ml":     round(kg_co2 / 2.31 * 1000, 1),  # mL of petrol
        "trees_days":    round(kg_co2 / 0.06,    1),   # tree-days to absorb
    }


# ─────────────────────────────────────────────
#  Gamification
# ─────────────────────────────────────────────

_TITLES = [
    (3.0,  "🌿 Eco Warrior",          "#16a34a", "You're a true environmental champion!"),
    (5.0,  "🍃 Green Champion",        "#22c55e", "Great work keeping emissions low!"),
    (7.0,  "♻️ Carbon Saver",          "#84cc16", "You're making a positive impact."),
    (9.0,  "🌱 Sustainability Leader",  "#eab308", "Good effort — keep pushing lower!"),
    (12.0, "☁️ Climate Guardian",       "#f97316", "Room to improve — try small changes."),
    (16.0, "⚡ Carbon Heavyweight",     "#ef4444", "High today — challenge yourself tomorrow."),
    (float("inf"), "🏭 Emission Titan", "#7f1d1d", "Critical level — take action today!"),
]

def get_eco_title(total_kg: float) -> tuple[str, str, str]:
    """Return (title, hex_color, message) for the given daily total emission."""
    for threshold, title, color, msg in _TITLES:
        if total_kg <= threshold:
            return title, color, msg
    return _TITLES[-1][1], _TITLES[-1][2], _TITLES[-1][3]


def get_streak(df) -> int:
    """Count consecutive days (from today backwards) with emissions logged."""
    if df.empty:
        return 0
    from datetime import date, timedelta
    dates = set(pd.to_datetime(df["date"]).dt.date)
    streak = 0
    check = date.today()
    while check in dates:
        streak += 1
        check -= timedelta(days=1)
    return streak


try:
    import pandas as pd
except ImportError:
    pass
