"""
pages/profile.py – Profile view and edit page.
"""

import streamlit as st
from database import get_user, save_user
from calculations import PC_FACTORS, AC_POWER_KW, MEAL_FACTORS, PRINTER_ELEC
from utils.components import page_header, section_title

DEPARTMENTS    = ["Mining","Excavation","Electrical","Mechanical","Civil","Environment","Safety","Finance","HR","Stores","IT","Administration","Survey","Other"]
TRANSPORT_MODES = ["Walking","Bicycle","Two-Wheeler","Car","Carpool","Bus","CNG Car"]
FUEL_TYPES     = ["Petrol","Diesel"]
PC_TYPES       = list(PC_FACTORS.keys())
AC_OPTIONS     = list(AC_POWER_KW.keys())
MEAL_OPTIONS   = list(MEAL_FACTORS.keys())
PRINTER_OPTS   = list(PRINTER_ELEC.keys())


def _idx(lst, val):
    try:
        return lst.index(val)
    except ValueError:
        return 0


def show_profile():
    user = st.session_state.user

    page_header(
        "My Profile",
        "View and update your permanent profile information",
        "👤"
    )

    # ── Current profile summary ──────────────────────────────────────
    section_title("Current Profile")

    info = {
        "👤 Employee ID":       user["employee_id"],
        "📛 Name":              user["name"],
        "🏢 Department":        user.get("department", "–"),
        "🚗 Transport Mode":    user.get("transport_mode", "–"),
        "⛽ Fuel Type":         user.get("fuel_type", "–"),
        "📐 Mileage":           f"{user.get('mileage', 0)} km/l",
        "📍 Commute Distance":  f"{user.get('commute_distance', 0)} km",
        "👥 Room Occupants":    user.get("room_occupants", 1),
        "💻 PC Type":           user.get("pc_type", "–"),
        "❄️ AC Tonnage":        user.get("ac_tonnage", "–"),
        "🥗 Meal Type":         user.get("meal_type", "–"),
        "🖨️ Printer Type":     user.get("printer_type", "–"),
    }

    # Two-column grid
    items = list(info.items())
    half = (len(items) + 1) // 2
    c1, c2 = st.columns(2)
    for label, value in items[:half]:
        with c1:
            st.markdown(f"""
            <div class="profile-item">
                <div class="pi-label">{label}</div>
                <div class="pi-val">{value}</div>
            </div>
            """, unsafe_allow_html=True)
    for label, value in items[half:]:
        with c2:
            st.markdown(f"""
            <div class="profile-item">
                <div class="pi-label">{label}</div>
                <div class="pi-val">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Edit form ────────────────────────────────────────────────────
    section_title("✏️ Edit Profile")

    with st.form("edit_profile"):
        c1, c2 = st.columns(2)
        with c1:
            name        = st.text_input("Full Name",   value=user["name"])
            department  = st.selectbox("Department",   DEPARTMENTS,
                                       index=_idx(DEPARTMENTS, user.get("department","")))
            transport_mode = st.selectbox("Transport Mode", TRANSPORT_MODES,
                                          index=_idx(TRANSPORT_MODES, user.get("transport_mode","Walking")))
        with c2:
            fuel_type = st.selectbox("Fuel Type", FUEL_TYPES,
                                     index=_idx(FUEL_TYPES, user.get("fuel_type","Petrol")),
                                     disabled=transport_mode not in ["Car","Carpool"])
            mileage = st.number_input("Mileage (km/l)", min_value=0.0,
                                      value=float(user.get("mileage") or 15.0), step=0.5)
            commute_distance = st.number_input("Home → Office (km)",
                                               min_value=0.0,
                                               value=float(user.get("commute_distance") or 0), step=0.5)

        w1, w2, w3 = st.columns(3)
        with w1:
            pc_type = st.selectbox("PC Type", PC_TYPES,
                                   index=_idx(PC_TYPES, user.get("pc_type","Laptop")))
        with w2:
            ac_tonnage = st.selectbox("AC Tonnage", AC_OPTIONS,
                                      index=_idx(AC_OPTIONS, user.get("ac_tonnage","No AC")))
        with w3:
            printer_type = st.selectbox("Printer Type", PRINTER_OPTS,
                                        index=_idx(PRINTER_OPTS, user.get("printer_type","None")))

        m1, m2 = st.columns(2)
        with m1:
            meal_type = st.selectbox("Meal Type", MEAL_OPTIONS,
                                     index=_idx(MEAL_OPTIONS, user.get("meal_type","Vegetarian")))
        with m2:
            room_occupants = st.number_input("Room Occupants", min_value=1, step=1,
                                             value=int(user.get("room_occupants") or 1))

        save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if save_btn:
            save_user(
                employee_id=user["employee_id"],
                name=name.strip(),
                department=department,
                transport_mode=transport_mode,
                fuel_type=fuel_type,
                mileage=mileage,
                commute_distance=commute_distance,
                room_occupants=room_occupants,
                pc_type=pc_type,
                ac_tonnage=ac_tonnage,
                meal_type=meal_type,
                printer_type=printer_type,
            )
            # Refresh session state
            st.session_state.user = get_user(user["employee_id"])
            st.success("✅ Profile updated successfully!")
            st.rerun()
