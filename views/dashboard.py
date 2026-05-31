"""
pages/dashboard.py – GHG Emissions Analytics Dashboard.

Displays today's KPIs, emission equivalents, eco-title, and
trend / breakdown charts (daily, weekly, monthly, pie, bar).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

from database import (
    get_emissions, get_today_emission,
    get_weekly_emission, get_monthly_emission,
)
from calculations import (
    emission_equivalents, get_eco_title, get_streak,
)
from utils.components import (
    page_header, metric_card, equiv_card,
    eco_title_banner, section_title,
)

# Consistent color palette
CAT_COLORS = {
    "Commute":       "#3b82f6",
    "Official Visit":"#0ea5e9",
    "AC":            "#14b8a6",
    "PC":            "#8b5cf6",
    "Meal":          "#f59e0b",
    "Printer":       "#78716c",
}
PLOTLY_TEMPLATE = "plotly_white"


def show_dashboard():
    user = st.session_state.user
    emp_id = user["employee_id"]

    page_header(
        "Emissions Dashboard",
        f"Your personal carbon footprint · {date.today().strftime('%d %B %Y')}",
        "🌱"
    )

    # ── Load data ────────────────────────────────────────────────────
    today_str = date.today().isoformat()
    today_row = get_today_emission(emp_id, today_str)
    df_all    = get_emissions(emp_id)
    df_week   = get_weekly_emission(emp_id)
    df_month  = get_monthly_emission(emp_id)

    # ── No data state ────────────────────────────────────────────────
    if df_all.empty:
        st.info(
            "No emission data yet. Head to **📅 Daily Log** to record your first day!",
            icon="🌱"
        )
        return

    # ── Eco title & streak ───────────────────────────────────────────
    streak = get_streak(df_all)

    if today_row:
        total_today = today_row["total_emission"]
        title, color, message = get_eco_title(total_today)
        eco_title_banner(title, color, message, streak)
    else:
        st.warning("📅 No entry for today. Log your activities to see today's title.", icon="⚠️")
        total_today = None

    # ── Today's KPI Cards ────────────────────────────────────────────
    if today_row:
        section_title("📊 Today's Emissions (kg CO₂e)")
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Total",          today_row["total_emission"],           "kg CO₂e", "🌍", "green")
        with c2: metric_card("Commute",         today_row["commute_emission"],         "kg CO₂e", "🚗", "blue")
        with c3: metric_card("AC",              today_row["ac_emission"],              "kg CO₂e", "❄️", "teal")
        with c4: metric_card("PC / Laptop",     today_row["pc_emission"],              "kg CO₂e", "💻", "purple")

        c5, c6, c7, c8 = st.columns(4)
        with c5: metric_card("Meal",            today_row["meal_emission"],            "kg CO₂e", "🥗", "amber")
        with c6: metric_card("Printer",         today_row["printer_emission"],         "kg CO₂e", "🖨️", "stone")
        with c7: metric_card("Official Visit",  today_row["official_visit_emission"],  "kg CO₂e", "🗺️", "red")
        with c8: metric_card("Days Logged",     len(df_all),                           "days",     "📆", "green")

        # ── Emission Equivalents ──────────────────────────────────────
        section_title("🔄 Real-World Equivalents")
        eq = emission_equivalents(total_today)
        e1, e2, e3, e4, e5, e6 = st.columns(6)
        with e1: equiv_card("🪨", eq["coal_g"],        "g of coal")
        with e2: equiv_card("🚬", eq["cigarettes"],    "cigarettes")
        with e3: equiv_card("📱", eq["phone_charges"], "phone charges")
        with e4: equiv_card("💡", eq["led_hours"],     "LED hours")
        with e5: equiv_card("⛽", eq["petrol_ml"],     "mL petrol")
        with e6: equiv_card("🌳", eq["trees_days"],    "tree-days")

    # ── Charts ───────────────────────────────────────────────────────
    section_title("📈 Trends & Breakdown")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📆 Daily Trend", "📅 Weekly", "📆 Monthly", "🍕 Breakdown"]
    )

    with tab1:
        _daily_trend_chart(df_all)

    with tab2:
        _weekly_stacked_chart(df_week)

    with tab3:
        _monthly_chart(df_month)

    with tab4:
        if today_row:
            _breakdown_charts(today_row, df_all)
        else:
            latest = df_all.iloc[-1]
            _breakdown_charts(dict(latest), df_all)

    # ── History table ─────────────────────────────────────────────────
    with st.expander("📋 Full Emission History"):
        display_df = df_all.copy()
        display_df.columns = [
            "Date", "Commute", "AC", "PC", "Meal",
            "Printer", "Official Visit", "Total"
        ]
        display_df = display_df.sort_values("Date", ascending=False)
        st.dataframe(
            display_df.style.format({
                c: "{:.3f}" for c in display_df.columns if c != "Date"
            }).background_gradient(subset=["Total"], cmap="RdYlGn_r"),
            use_container_width=True,
            hide_index=True,
        )


# ── Individual chart helpers ─────────────────────────────────────────

def _daily_trend_chart(df: pd.DataFrame):
    if df.empty:
        st.info("No data available yet.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["total_emission"],
        mode="lines+markers",
        name="Daily Total",
        line=dict(color="#16a34a", width=2.5),
        marker=dict(size=7, color="#16a34a"),
        fill="tozeroy",
        fillcolor="rgba(34,197,94,0.08)",
    ))

    # 7-day rolling average
    if len(df) >= 3:
        df = df.copy()
        df["rolling"] = df["total_emission"].rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["rolling"],
            mode="lines",
            name="7-day avg",
            line=dict(color="#f59e0b", width=1.5, dash="dash"),
        ))

    fig.update_layout(
        title="Daily CO₂ Emissions",
        xaxis_title="Date",
        yaxis_title="kg CO₂e",
        template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=50, b=40),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)


def _weekly_stacked_chart(df: pd.DataFrame):
    if df.empty:
        st.info("No data for the last 7 days.")
        return

    cats = [
        ("commute_emission",        "Commute",        CAT_COLORS["Commute"]),
        ("official_visit_emission", "Official Visit", CAT_COLORS["Official Visit"]),
        ("ac_emission",             "AC",             CAT_COLORS["AC"]),
        ("pc_emission",             "PC",             CAT_COLORS["PC"]),
        ("meal_emission",           "Meal",           CAT_COLORS["Meal"]),
        ("printer_emission",        "Printer",        CAT_COLORS["Printer"]),
    ]

    fig = go.Figure()
    for col, label, color in cats:
        if col in df.columns:
            fig.add_trace(go.Bar(
                x=df["date"], y=df[col],
                name=label, marker_color=color
            ))

    fig.update_layout(
        barmode="stack",
        title="Last 7 Days – Category Breakdown",
        xaxis_title="Date",
        yaxis_title="kg CO₂e",
        template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=50, b=40),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)


def _monthly_chart(df: pd.DataFrame):
    if df.empty:
        st.info("No monthly data available.")
        return

    fig = px.bar(
        df, x="month", y="total_emission",
        labels={"total_emission": "kg CO₂e", "month": "Month"},
        title="Monthly Emission Totals",
        color="total_emission",
        color_continuous_scale=["#dcfce7", "#16a34a", "#14532d"],
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        coloraxis_showscale=False,
        margin=dict(t=50, b=40),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)


def _breakdown_charts(row: dict, df_all: pd.DataFrame):
    components = {
        "Commute":        row.get("commute_emission", 0),
        "Official Visit": row.get("official_visit_emission", 0),
        "AC":             row.get("ac_emission", 0),
        "PC":             row.get("pc_emission", 0),
        "Meal":           row.get("meal_emission", 0),
        "Printer":        row.get("printer_emission", 0),
    }
    # Filter out zero values for cleaner pie
    components = {k: v for k, v in components.items() if v > 0}

    c1, c2 = st.columns(2)

    with c1:
        if components:
            fig_pie = go.Figure(go.Pie(
                labels=list(components.keys()),
                values=list(components.values()),
                marker_colors=[CAT_COLORS[k] for k in components],
                hole=0.45,
                textinfo="label+percent",
            ))
            fig_pie.update_layout(
                title="Category Distribution",
                template=PLOTLY_TEMPLATE,
                showlegend=False,
                margin=dict(t=50, b=20, l=10, r=10),
                height=320,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        # Horizontal bar – all history averages per category
        if not df_all.empty:
            avg = {
                "Commute":        df_all["commute_emission"].mean(),
                "Official Visit": df_all["official_visit_emission"].mean(),
                "AC":             df_all["ac_emission"].mean(),
                "PC":             df_all["pc_emission"].mean(),
                "Meal":           df_all["meal_emission"].mean(),
                "Printer":        df_all["printer_emission"].mean(),
            }
            fig_bar = px.bar(
                x=list(avg.values()),
                y=list(avg.keys()),
                orientation="h",
                color=list(avg.keys()),
                color_discrete_map=CAT_COLORS,
                title="Historical Category Averages",
                labels={"x": "avg kg CO₂e / day", "y": ""},
            )
            fig_bar.update_layout(
                template=PLOTLY_TEMPLATE,
                showlegend=False,
                margin=dict(t=50, b=20, l=10, r=10),
                height=320,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
