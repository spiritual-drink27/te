"""
pages/daily_log.py – Daily GHG activity log form.

Responsibilities:
  - Render daily input form (pre-filled from profile)
  - Allow one-day overrides without touching profile
  - Calculate and upsert emissions for the selected date
  - Display quick result summary after submission
"""

import streamlit as st
from datetime import datetime, date

from calculations import (
    calculate_emissions,
    emission_equivalents,
    get_eco_title,
    get_streak,
    PC_FACTORS, AC_POWER_KW, MEAL_FACTORS, PRINTER_ELEC,
)
from database import upsert_emission, get_emissions, get_today_emission
from utils.components import (
    page_header, metric_card, equiv_card, eco_title_banner, section_title
)

TRANSPORT_MODES = ["Walking", "Bicycle", "Two-Wheeler", "Car", "Carpool", "Bus", "CNG Car"]
FUEL_TYPES      = ["Petrol", "Diesel"]
PC_TYPES        = list(PC_FACTORS.keys())
AC_OPTIONS      = list(AC_POWER_KW.keys())
MEAL_OPTIONS    = list(MEAL_FACTORS.keys())
PRINTER_OPTS    = list(PRINTER_ELEC.keys())


def _idx(lst: list, val):
    """Safe index lookup with fallback to 0."""
    try:
        return lst.index(val)
    except ValueError:
        return 0


def show_daily_log():
    user = st.session_state.user

    page_header(
        "Daily Activity Log",
        f"Log your activities for today · {date.today().strftime('%A, %d %B %Y')}",
        "📅"
    )

    # ── Check if already logged today ──────────────────────────────
    today_str = date.today().isoformat()
    today_log = get_today_emission(user["employee_id"], today_str)
    if today_log:
        st.info(
            f"✅ You've already logged today ({date.today().strftime('%d %b %Y')}). "
            "Submitting again will **update** today's record.",
            icon="ℹ️"
        )

    with st.form("daily_form", clear_on_submit=False):

        # ── Section: Commute ────────────────────────────────────────
        section_title("🚗 Commute")
        c1, c2, c3 = st.columns(3)
        with c1:
            log_date = st.date_input("Date", value=date.today(), max_value=date.today())
        with c2:
            transport_mode = st.selectbox(
                "Transport Mode", TRANSPORT_MODES,
                index=_idx(TRANSPORT_MODES, user.get("transport_mode", "Walking"))
            )
        with c3:
            commute_distance = st.number_input(
                "One-way Distance (km)",
                min_value=0.0, step=0.5,
                value=float(user.get("commute_distance") or 0)
            )

        # Conditional car fields
        is_car = transport_mode in ["Car", "Carpool"]
        car_c1, car_c2, car_c3 = st.columns(3)
        with car_c1:
            fuel_type = st.selectbox(
                "Fuel Type", FUEL_TYPES,
                index=_idx(FUEL_TYPES, user.get("fuel_type", "Petrol")),
                disabled=not is_car
            )
        with car_c2:
            mileage = st.number_input(
                "Mileage (km/l)", min_value=0.0, step=0.5,
                value=float(user.get("mileage") or 15.0),
                disabled=not is_car
            )
        with car_c3:
            persons_in_car = st.number_input(
                "Persons in car", min_value=1, step=1,
                value=1,
                disabled=(transport_mode != "Carpool")
            )

        official_visit_km = st.number_input(
            "Official Visit Distance (km, one-way, if any)", min_value=0.0, value=0.0, step=0.5
        )

        st.markdown('<hr class="ghg-divider">', unsafe_allow_html=True)

        # ── Section: Workplace ──────────────────────────────────────
        section_title("🏢 Workplace Equipment")
        w1, w2, w3, w4 = st.columns(4)
        with w1:
            pc_type = st.selectbox(
                "PC / Laptop", PC_TYPES,
                index=_idx(PC_TYPES, user.get("pc_type", "Laptop"))
            )
        with w2:
            pc_hours = st.number_input("PC Usage (hrs)", min_value=0.0, max_value=12.0, value=8.0, step=0.5)
        with w3:
            ac_tonnage = st.selectbox(
                "AC", AC_OPTIONS,
                index=_idx(AC_OPTIONS, user.get("ac_tonnage", "No AC"))
            )
        with w4:
            ac_hours = st.number_input("AC Usage (hrs)", min_value=0.0, max_value=12.0, value=8.0, step=0.5)

        p1, p2 = st.columns(2)
        with p1:
            printer_type = st.selectbox(
                "Printer Type", PRINTER_OPTS,
                index=_idx(PRINTER_OPTS, user.get("printer_type", "None"))
            )
        with p2:
            pages_printed = st.number_input("Pages Printed", min_value=0, value=0, step=1)

        st.markdown('<hr class="ghg-divider">', unsafe_allow_html=True)

        # ── Section: Meals ──────────────────────────────────────────
        section_title("🥗 Meals")
        meal_type = st.selectbox(
            "Lunch Type",
            MEAL_OPTIONS,
            index=_idx(MEAL_OPTIONS, user.get("meal_type", "Vegetarian"))
        )

        submitted = st.form_submit_button(
            "🌍 Calculate & Save Emissions", use_container_width=True
        )

    # ── Handle submission ────────────────────────────────────────────
    if submitted:
        result = calculate_emissions(
            transport_mode=transport_mode,
            commute_distance=commute_distance,
            fuel_type=fuel_type,
            mileage=mileage,
            persons_in_car=int(persons_in_car),
            official_visit_km=official_visit_km,
            pc_type=pc_type,
            pc_hours=pc_hours,
            ac_tonnage=ac_tonnage,
            ac_hours=ac_hours,
            meal_type=meal_type,
            printer_type=printer_type,
            pages_printed=int(pages_printed),
        )

        upsert_emission(
            employee_id=user["employee_id"],
            date=log_date.isoformat(),
            commute=result.commute,
            ac=result.ac,
            pc=result.pc,
            meal=result.meal,
            printer=result.printer,
            official_visit=result.official_visit,
            total=result.total,
        )

        # Refresh session user for sidebar cache
        st.session_state.last_emission = result

        st.success("✅ Emissions saved successfully!")
        # _show_result_summary(result, user["employee_id"])
        st.session_state.page = "dashboard"
        st.rerun()