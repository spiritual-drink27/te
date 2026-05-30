"""
utils/components.py – Reusable HTML/Streamlit UI components.
"""

import streamlit as st


# ── Page header banner ──────────────────────────────────────────────
def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(f"""
    <div class="ghg-header">
        <div>
            <h1>{icon}&nbsp;&nbsp;{title}</h1>
            <div class="subtitle">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Metric card ─────────────────────────────────────────────────────
def metric_card(label: str, value, unit: str = "", icon: str = "",
                color: str = "green"):
    if isinstance(value, float):
        display = f"{value:.3f}" if value < 10 else f"{value:.2f}"
    else:
        display = str(value)
    st.markdown(f"""
    <div class="metric-card {color}">
        <span class="icon">{icon}</span>
        <div class="label">{label}</div>
        <div class="value">{display}</div>
        <div class="unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Emission equivalents card ────────────────────────────────────────
def equiv_card(icon: str, value, label: str):
    if isinstance(value, float):
        display = f"{value:,.1f}"
    else:
        display = str(value)
    st.markdown(f"""
    <div class="equiv-card">
        <div class="eq-icon">{icon}</div>
        <div class="eq-val">{display}</div>
        <div class="eq-lbl">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Leaderboard row ──────────────────────────────────────────────────
def lb_row(rank: int, name: str, dept: str, value: float, title: str):
    medal = {1: "gold", 2: "silver", 3: "bronze"}.get(rank, "")
    emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
    st.markdown(f"""
    <div class="lb-row {medal}">
        <div class="lb-rank">{emoji}</div>
        <div>
            <div class="lb-name">{name}</div>
            <div class="lb-dept">{dept} · {title}</div>
        </div>
        <div style="margin-left:auto; text-align:right">
            <div class="lb-val">{value:.3f}</div>
            <div class="lb-unit">kg CO₂e</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Eco title banner ─────────────────────────────────────────────────
def eco_title_banner(title: str, color: str, message: str, streak: int = 0):
    streak_html = (
        f'<span class="streak-badge">🔥 {streak}-day streak</span>'
        if streak > 0 else ""
    )
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color}22,{color}11);
                border:2px solid {color}55; border-radius:14px;
                padding:20px 24px; text-align:center; margin-bottom:20px;">
        <div style="font-size:32px; font-weight:900; color:{color}; 
                    letter-spacing:.02em;">{title}</div>
        <div style="font-size:13px; color:#374151; margin-top:6px;">{message}</div>
        <div style="margin-top:10px;">{streak_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Section title ────────────────────────────────────────────────────
def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


# ── Profile sidebar info ─────────────────────────────────────────────
def profile_item(label: str, value):
    st.markdown(f"""
    <div class="profile-item">
        <div class="pi-label">{label}</div>
        <div class="pi-val">{value}</div>
    </div>
    """, unsafe_allow_html=True)
