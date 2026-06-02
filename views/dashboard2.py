import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

from database import (
    get_emissions, get_today_emission,
    get_weekly_emission, get_monthly_emission,
)
from calculations import emission_equivalents, get_eco_title, get_streak
from utils.components import section_title

CAT_COLORS = {
    "Commute":        "#3b82f6",
    "Official Visit": "#0ea5e9",
    "AC":             "#14b8a6",
    "PC":             "#8b5cf6",
    "Meal":           "#f59e0b",
    "Printer":        "#78716c",
}
PLOTLY_TEMPLATE = "plotly_white"
MAX_DAILY_KG = 20.0   # gauge full-scale


# ── CSS injected once ────────────────────────────────────────────────
_DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

.db-wrap { font-family: 'DM Sans', sans-serif; }

/* ── Eco title card ── */
.eco-hero {
    border-radius: 20px;
    padding: 28px 32px;
    text-align: center;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
}
.eco-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: inherit;
    filter: blur(0);
    z-index: 0;
}
.eco-hero-title {
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -.01em;
    position: relative;
    z-index: 1;
}
.eco-hero-msg {
    font-size: 13px;
    opacity: .8;
    margin-top: 4px;
    position: relative;
    z-index: 1;
}
.eco-hero-streak {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(0,0,0,.15);
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 10px;
    position: relative;
    z-index: 1;
}

/* ── Time range pills ── */
.range-wrap {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin: 18px 0 4px;
}

/* ── Stat pills below gauge ── */
.stat-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 12px;
}
.stat-pill {
    background: #ffffff;
    border: 1px solid #e7f5eb;
    border-radius: 12px;
    padding: 10px 16px;
    text-align: center;
    min-width: 80px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.stat-pill .sp-val {
    font-size: 18px;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
    color: #052e16;
    line-height: 1;
}
.stat-pill .sp-lbl {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .07em;
    color: #6b7280;
    margin-top: 3px;
}
.stat-pill.accent { border-top: 3px solid #22c55e; }

/* ── Equiv cards ── */
.eq-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 4px;
}
.eq-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 14px 10px;
    text-align: center;
    border: 1px solid #e7f5eb;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.eq-card .ec-icon { font-size: 26px; }
.eq-card .ec-val  {
    font-size: 19px; font-weight: 700;
    font-family: 'DM Mono', monospace;
    color: #052e16; margin-top: 4px; line-height: 1;
}
.eq-card .ec-lbl  {
    font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: .07em;
    color: #6b7280; margin-top: 3px;
}

/* ── Section label ── */
.db-section {
    font-size: 13px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .08em;
    color: #6b7280; margin: 22px 0 10px;
}
</style>
"""


def show_dashboard():
    user   = st.session_state.user
    emp_id = user["employee_id"]

    st.markdown(_DASHBOARD_CSS, unsafe_allow_html=True)
    st.markdown('<div class="db-wrap">', unsafe_allow_html=True)

    # ── Load data ────────────────────────────────────────────────────
    today_str = date.today().isoformat()
    today_row = get_today_emission(emp_id, today_str)
    df_all    = get_emissions(emp_id)
    df_week   = get_weekly_emission(emp_id)
    df_month  = get_monthly_emission(emp_id)

    if df_all.empty and not today_row:
        st.info("No emission data yet. Head to **📅 Daily Log** to record your first day!", icon="🌱")
        return

    # ── Eco title hero ───────────────────────────────────────────────
    streak = get_streak(df_all)
    if today_row:
        total_today = today_row["total_emission"]
        title, color, message = get_eco_title(total_today)
    else:
        total_today = None
        title, color, message = "🌱 No Entry Today", "#16a34a", "Log today's activities below"

    streak_html = f'<div class="eco-hero-streak">🔥 {streak}-day streak</div>' if streak > 0 else ""
    st.markdown(f"""
    <div class="eco-hero" style="background:linear-gradient(135deg,{color}22,{color}44);
         border: 2px solid {color}55; color: #052e16;">
        <div class="eco-hero-title" style="color:{color}">{title}</div>
        <div class="eco-hero-msg">{message}</div>
        {streak_html}
    </div>
    """, unsafe_allow_html=True)

    # ── Time range switcher ──────────────────────────────────────────
    st.markdown('<div class="db-section">📊 Emission Overview</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        range_sel = st.selectbox(
        "Time Range",
        ["Today", "This Week", "This Month"],
        label_visibility="collapsed",
        key="dash_range"
        )

    # ── Main visual based on range ───────────────────────────────────
    if range_sel == "Today":
        _show_today(today_row, total_today, color)

    elif range_sel == "This Week":
        _show_weekly(df_week)

    else:
        _show_monthly(df_month)

    # ── Emission Equivalents ─────────────────────────────────────────
    if total_today:
        st.markdown('<div class="db-section">🔄 Real-World Equivalents</div>', unsafe_allow_html=True)
        eq = emission_equivalents(total_today)
        eq_data = [
            ("🪨", eq["coal_g"],        "g Coal"),
            ("🚬", eq["cigarettes"],    "Cigarettes"),
            ("📱", eq["phone_charges"], "Phone Charges"),
            ("💡", eq["led_hours"],     "LED Hours"),
            ("⛽", eq["petrol_ml"],     "mL Petrol"),
            ("🌳", eq["trees_days"],    "Tree-Days"),
        ]
        st.markdown('<div class="eq-grid">', unsafe_allow_html=True)
        # Split into two rows of 3 using columns
        row1 = st.columns(3)
        row2 = st.columns(3)
        for i, (icon, val, lbl) in enumerate(eq_data):
            col = row1[i] if i < 3 else row2[i - 3]
            with col:
                st.markdown(f"""
                <div class="eq-card">
                    <div class="ec-icon">{icon}</div>
                    <div class="ec-val">{val:,.1f}</div>
                    <div class="ec-lbl">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Full history ─────────────────────────────────────────────────
    st.markdown('<div class="db-section">📋 Emission History</div>', unsafe_allow_html=True)
    with st.expander("View full history", expanded=False):
        if df_all.empty:
            st.info("No history yet.")
        else:
            display_df = df_all.copy()
            display_df.columns = [
                "Date", "Commute", "AC", "PC", "Meal",
                "Printer", "Official Visit", "Total"
            ]
            display_df = display_df.sort_values("Date", ascending=False)
            st.dataframe(
                display_df.style.format({
                    c: "{:.2f}" for c in display_df.columns if c != "Date"
                }).background_gradient(subset=["Total"], cmap="RdYlGn_r"),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)


# ── Today view: circular gauge + category breakdown ──────────────────
def _show_today(today_row, total_today, color):
    if not today_row:
        st.markdown("""
        <div style="text-align:center; padding:40px 0; color:#374151;">
            <div style="font-size:48px;">📅</div>
            <div style="font-size:15px; margin-top:8px; font-weight:500;">No entry for today yet</div>
            <div style="font-size:13px; margin-top:4px;">Go to Daily Log to record your activities</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Circular gauge
    pct = min(total_today / MAX_DAILY_KG, 1.0)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(total_today, 2),
        number={"suffix": " kg", "font": {"size": 36, "family": "DM Mono", "color": "#052e16"}},
        gauge={
            "axis": {"range": [0, MAX_DAILY_KG], "tickwidth": 1, "tickcolor": "#5060f0",
                     "tickfont": {"size": 10, "color": "#405785"}},
            "bar":  {"color": color, "thickness": 0.22},
            "bgcolor": "#c7f1d4",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  3],  "color": "#dcfce7"},
                {"range": [3,  7],  "color": "#bbf7d0"},
                {"range": [7,  12], "color": "#fef9c3"},
                {"range": [12, 16], "color": "#fed7aa"},
                {"range": [16, 20], "color": "#fecaca"},
            ],
            "threshold": {
                "line": {"color": "#ef4444", "width": 3},
                "thickness": 0.75,
                "value": 16
            },
        },
        title={"text": "Today's CO₂e", "font": {"size": 14, "color": "#6b7280", "family": "DM Sans"}},
        domain={"x": [0.1, 0.9], "y": [0, 1]},
    ))
    fig.update_layout(
        height=280,
        margin=dict(t=30, b=0, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans"},
    )

    _, gcol, _ = st.columns([1, 2, 1])
    with gcol:
        st.plotly_chart(fig, use_container_width=True)

    # Stat pills
    cats = {
        "🚗 Commute":  today_row["commute_emission"],
        "❄️ AC":       today_row["ac_emission"],
        "💻 PC":       today_row["pc_emission"],
        "🥗 Meal":     today_row["meal_emission"],
        "🖨️ Printer":  today_row["printer_emission"],
        "🗺️ Official": today_row["official_visit_emission"],
    }
    cols = st.columns(6)
    for col, (lbl, val) in zip(cols, cats.items()):
        with col:
            st.markdown(f"""
            <div class="stat-pill accent">
                <div class="sp-val">{val:.2f}</div>
                <div class="sp-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    # Donut breakdown
    st.markdown('<div style="margin-top:20px"></div>', unsafe_allow_html=True)
    components = {k.split(" ", 1)[1]: v for k, v in cats.items() if v > 0}
    color_map = {"Commute": "#3b82f6", "AC": "#14b8a6", "PC": "#8b5cf6",
                 "Meal": "#f59e0b", "Printer": "#78716c", "Official": "#0ea5e9"}

    if components:
        fig_donut = go.Figure(go.Pie(
            labels=list(components.keys()),
            values=list(components.values()),
            marker_colors=[color_map.get(k, "#22c55e") for k in components],
            hole=0.55,
            textinfo="label+percent",
            textfont={"size": 12, "family": "DM Sans", "color": "#405785"},
            hovertemplate="%{label}: %{value:.3f} kg<extra></extra>",
        ))
        fig_donut.add_annotation(
            text=f"{total_today:.2f}<br>kg CO₂e",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "family": "DM Mono", "color": "#052e16"},
        )
        fig_donut.update_layout(
            title={"text": "Category Breakdown", "font": {"size": 14, "color": "#6b7280"}},
            template=PLOTLY_TEMPLATE,
            showlegend=True,
            legend={"orientation": "h", "yanchor": "bottom", "y": -0.4},
            margin=dict(t=40, b=40, l=10, r=10),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_donut, use_container_width=True)


# ── Weekly view: Mon–Sun bar chart ──────────────────────────────────
def _show_weekly(df_week: pd.DataFrame):
    # Build full Mon–Sun scaffold for current week
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    if not df_week.empty:
        df_week = df_week.copy()
        df_week["date"] = pd.to_datetime(df_week["date"]).dt.date
        date_map = dict(zip(df_week["date"], df_week["total_emission"]))
    else:
        date_map = {}

    values = [date_map.get(d, 0.0) for d in week_dates]
    colors = [
        "#22c55e" if v <= 5
        else "#f59e0b" if v <= 10
        else "#ef4444"
        for v in values
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=day_labels,
        y=values,
        marker_color=colors,
        marker_line_width=0,
        text=[f"{v:.1f}" if v > 0 else "" for v in values],
        textposition="outside",
        textfont={"family": "DM Mono", "size": 11},
        hovertemplate="%{x}: %{y:.3f} kg CO₂e<extra></extra>",
    ))

    # Highlight today
    today_idx = today.weekday()
    fig.add_shape(
        type="rect",
        x0=today_idx - 0.4, x1=today_idx + 0.4,
        y0=0, y1=max(values) * 1.15 if max(values) > 0 else 1,
        fillcolor="rgba(34,197,94,.08)",
        line=dict(color="#22c55e", width=1.5, dash="dot"),
    )
    fig.add_annotation(
        x=today_idx, y=max(values) * 1.12 if max(values) > 0 else 0.9,
        text="today", showarrow=False,
        font={"size": 10, "color": "#16a34a", "family": "DM Sans"},
    )

    fig.update_layout(
        title={"text": f"Week of {monday.strftime('%d %b')}",
               "font": {"size": 14, "color": "#0d1320", "family": "DM Sans"}},
        yaxis_title="kg CO₂e",
        xaxis={"tickfont": {"color": "#111827", "size": 12, "family": "DM Sans"}},
        yaxis={"gridcolor": "#f0fdf4", "tickfont": {"color": "#111827", "size": 11}},
        template=PLOTLY_TEMPLATE,
        margin=dict(t=50, b=20, l=10, r=10),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # yaxis={"gridcolor": "#f0fdf4"},
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Weekly total + avg pills
    total_wk = sum(values)
    logged    = sum(1 for v in values if v > 0)
    avg_wk    = total_wk / logged if logged > 0 else 0

    c1, c2, c3 = st.columns(3)
    for col, (lbl, val, unit) in zip([c1, c2, c3], [
        ("Weekly Total", f"{total_wk:.2f}", "kg CO₂e"),
        ("Daily Average", f"{avg_wk:.2f}", "kg CO₂e"),
        ("Days Logged",  str(logged),      f"/ 7 days"),
    ]):
        with col:
            st.markdown(f"""
            <div class="stat-pill accent" style="min-width:unset">
                <div class="sp-val">{val}</div>
                <div class="sp-lbl">{lbl} · {unit}</div>
            </div>
            """, unsafe_allow_html=True)


# ── Monthly view ─────────────────────────────────────────────────────
def _show_monthly(df_month: pd.DataFrame):
    # Build full 12-month scaffold
    current_year = date.today().year
    all_months = [f"{current_year}-{m:02d}" for m in range(1, 13)]
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    if not df_month.empty:
        month_map = dict(zip(df_month["month"], df_month["total_emission"]))
    else:
        month_map = {}

    values = [month_map.get(m, 0.0) for m in all_months]
    colors = [
        "#22c55e" if v <= 30
        else "#f59e0b" if v <= 60
        else "#ef4444"
        for v in values
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=month_labels,
        y=values,
        marker_color=colors,
        marker_line_width=0,
        text=[f"{v:.1f}" if v > 0 else "–" for v in values],
        textposition="inside",
        insidetextanchor="middle",
        textfont={"family": "DM Mono", "size": 11, "color": "#ffffff"},
        hovertemplate="%{x}: %{y:.2f} kg CO₂e<extra></extra>",
    ))

    fig.update_layout(
        title={"text": f"Monthly Totals – {current_year}",
               "font": {"size": 14, "color": "#6b7280", "family": "DM Sans"}},
        template=PLOTLY_TEMPLATE,
        margin=dict(t=50, b=20, l=10, r=10),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"tickfont": {"color": "#111827", "size": 12, "family": "DM Sans"},
               "gridcolor": "rgba(0,0,0,0)"},
        yaxis={"tickfont": {"color": "#111827", "size": 11},
               "gridcolor": "#f0fdf4",
               "range": [0, max(max(values), 1) * 1.3]},
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Monthly stats
    logged_months = [(m, v) for m, v in zip(month_labels, values) if v > 0]
    if logged_months:
        best_lbl  = min(logged_months, key=lambda x: x[1])
        worst_lbl = max(logged_months, key=lambda x: x[1])
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="stat-pill accent">
                <div class="sp-val">{sum(values):.1f}</div>
                <div class="sp-lbl">Total · kg CO₂e</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="stat-pill accent">
                <div class="sp-val">{best_lbl[0]}</div>
                <div class="sp-lbl">🏆 Best Month</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="stat-pill accent">
                <div class="sp-val">{worst_lbl[0]}</div>
                <div class="sp-lbl">⚡ Highest Month</div></div>""", unsafe_allow_html=True)
    else:
        st.info("No monthly data logged yet.", icon="📆")