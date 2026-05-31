"""
pages/auth.py – Login and Registration pages.
"""

import streamlit as st
from database import get_user, save_user
from utils.components import page_header

DEPARTMENTS = [
    "Mining", "Excavation", "Electrical", "Mechanical", "Civil",
    "Environment", "Safety", "Finance", "HR", "Stores", "IT",
    "Administration", "Survey", "Other",
]
TRANSPORT_MODES = [
    "Walking", "Bicycle", "Two-Wheeler", "Car", "Carpool", "Bus", "CNG Car",
]
FUEL_TYPES   = ["Petrol", "Diesel"]
PC_TYPES     = ["Laptop", "Desktop", "Desktop + Monitor", "Laptop + Monitor"]
AC_OPTIONS   = ["No AC", "1.0 Ton", "1.5 Ton", "2.0 Ton"]
MEAL_OPTIONS = ["Vegetarian", "Non-Vegetarian"]
PRINTER_OPTS = ["None", "Inkjet", "Laser", "Office Copier"]


def show_login():
    from PIL import Image
    img=Image.open("assets/logo.jpeg")
    st.image(img, width=150)

    st.markdown("""
<div class="login-wrap">
    <div class="login-logo">🌱</div>
    <div class="login-title">GHG Tracker</div>
    <div style="font-size:15px; font-weight:800; color:#15803d; text-align:center; 
                letter-spacing:.06em; text-transform:uppercase; margin-bottom:4px;">
        CIL Sonepur Bazari Area
    </div>
    <div class="login-sub">🌍 World Environment Day Initiative</div>
</div>
""", unsafe_allow_html=True)

    # Centre the form
    _, col, _ = st.columns([1, 2, 1])
    with col:
        emp_id = st.text_input("Employee ID", placeholder="e.g. 8135431385")
        name   = st.text_input("Full Name",   placeholder="e.g. Ramesh Kumar")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔐 Login", use_container_width=True, type="primary"):
                _handle_login(emp_id, name)
        with c2:
            if st.button("📝 Register", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()


def _handle_login(emp_id: str, name: str):
    emp_id = emp_id.strip()
    name   = name.strip()
    if not emp_id or not name:
        st.error("Please enter both Employee ID and Name.")
        return
    user = get_user(emp_id)
    if user and user["name"].lower() == name.lower():
        st.session_state.logged_in   = True
        st.session_state.employee_id = emp_id
        st.session_state.user        = user
        st.session_state.page        = "daily_log"
        st.rerun()
    else:
        st.error("Invalid credentials. Check your Employee ID and Name, or register first.")


def show_register():
    page_header("Employee Registration", "Create your profile to start tracking", "📝")

    with st.form("reg_form"):
        st.markdown("#### Personal Details")
        c1, c2 = st.columns(2)
        with c1:
            employee_id = st.text_input("Employee ID *")
            name        = st.text_input("Full Name *")
            department  = st.selectbox("Department", DEPARTMENTS)
        with c2:
            room_occupants = st.number_input(
                "People sharing your room/cabin", min_value=1, value=1, step=1
            )

        st.markdown("#### 🚗 Commute")
        c1, c2, c3 = st.columns(3)
        with c1:
            transport_mode = st.selectbox("Primary Mode", TRANSPORT_MODES)
        with c2:
            fuel_type = st.selectbox("Fuel Type", FUEL_TYPES,
                                     disabled=transport_mode not in ["Car", "Carpool"])
        with c3:
            mileage = st.number_input(
                "Mileage (km/l)", min_value=0.0, value=15.0, step=0.5,
                disabled=transport_mode not in ["Car", "Carpool", "CNG Car", "Two-Wheeler"]
            )
        commute_distance = st.number_input(
            "Home → Office Distance (km, one way)", min_value=0.0, value=10.0, step=0.5
        )

        st.markdown("#### 💻 Workplace Equipment")
        c1, c2, c3 = st.columns(3)
        with c1:
            pc_type     = st.selectbox("PC / Laptop Type", PC_TYPES)
        with c2:
            ac_tonnage  = st.selectbox("AC Tonnage", AC_OPTIONS)
        with c3:
            printer_type = st.selectbox("Printer Type", PRINTER_OPTS)

        st.markdown("#### 🥗 Meals")
        meal_type = st.selectbox("Typical Lunch Type", MEAL_OPTIONS)

        submitted = st.form_submit_button("✅ Register", use_container_width=True)

        if submitted:
            employee_id = employee_id.strip()
            name        = name.strip()
            if not employee_id or not name:
                st.error("Employee ID and Name are required.")
            elif get_user(employee_id):
                st.warning("This Employee ID already exists. Use Login or contact admin.")
            else:
                save_user(
                    employee_id=employee_id,
                    name=name,
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
                st.success("✅ Registration successful! Please login.")
                st.session_state.page = "login"
                st.rerun()

    if st.button("← Back to Login"):
        st.session_state.page = "login"
        st.rerun()
