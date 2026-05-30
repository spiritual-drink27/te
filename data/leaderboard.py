"""
pages/leaderboard.py – Employee Leaderboard (Daily & Weekly).
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date

from database import get_daily_leaderboard, get_weekly_leaderboard
from calculations import get_eco_title, emission_equivalents
from utils.components import page_header, section_title, lb_row

PLOTLY_TEMPLATE = "plotly_white"


def _enrich(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Add rank, eco title, and coal equivalent columns."""
    df = df.copy()
    df = df.sort_values(value_col)
    df = df.reset_index(drop=True)
    df["rank"] = df.index + 1

    df["eco_title"] = df[value_col].apply(lambda v: get_eco_title(v)[0])
    df["coal_g"]    = df[value_col].apply(
        lambda v: emission_equivalents(v)["coal_g"]
    )
    return df


def show_leaderboard():
    page_header(
        "Employee Leaderboard",
        "Lower emissions = better rank · CIL Sonpur Bazari Area",
        "🏆"
    )

    tab1, tab2 = st.tabs(["📅 Today's Ranking", "📆 Weekly Ranking"])

    today_str = date.today().isoformat()

    with tab1:
        df = get_daily_leaderboard(today_str)
        if df.empty or df["daily_emission"].sum() == 0:
            st.info("No one has logged emissions today yet. Be the first! 🌱", icon="📅")
        else:
            df = _enrich(df, "daily_emission")
            _render_leaderboard(df, "daily_emission", "Today's Emission")

    with tab2:
        df = get_weekly_leaderboard()
        if df.empty or df["weekly_emission"].sum() == 0:
            st.info("No weekly data available yet.", icon="📆")
        else:
            df = _enrich(df, "weekly_emission")
            _render_leaderboard(df, "weekly_emission", "Weekly Total Emission")


def _render_leaderboard(df: pd.DataFrame, value_col: str, label: str):
    # ── Top-3 highlight ──────────────────────────────────────────────
    if len(df) >= 1:
        section_title("🌟 Top Performers")
        top = df.head(3)
        cols = st.columns(min(len(top), 3))
        medals = ["🥇", "🥈", "🥉"]
        bg_colors = ["#fffbeb", "#f8fafc", "#fefce8"]
        border_colors = ["#f59e0b", "#94a3b8", "#ca8a04"]

        for i, (_, row) in enumerate(top.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div style="background:{bg_colors[i]};
                            border:2px solid {border_colors[i]};
                            border-radius:14px; padding:20px;
                            text-align:center;">
                    <div style="font-size:36px">{medals[i]}</div>
                    <div style="font-weight:800; font-size:15px; color:#111827; margin-top:6px">{row['name']}</div>
                    <div style="font-size:12px; color:#6b7280;">{row['department']}</div>
                    <div style="font-size:22px; font-weight:900; color:#15803d; margin-top:10px;
                                font-family:'JetBrains Mono',monospace">{row[value_col]:.3f}</div>
                    <div style="font-size:11px; color:#6b7280">kg CO₂e</div>
                    <div style="margin-top:8px; font-size:12px; color:#374151">{row['eco_title']}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Full ranking list ────────────────────────────────────────────
    section_title(f"📋 Full Rankings – {label}")
    for _, row in df.iterrows():
        lb_row(
            rank=int(row["rank"]),
            name=row["name"],
            dept=row["department"],
            value=row[value_col],
            title=row["eco_title"],
        )

    # ── Bar chart ────────────────────────────────────────────────────
    section_title("📊 Visual Comparison")
    display_df = df.copy()
    display_df["label"] = display_df.apply(
        lambda r: f"{r['name']} ({r['department'][:3]})", axis=1
    )

    fig = px.bar(
        display_df,
        x="label",
        y=value_col,
        color=value_col,
        color_continuous_scale=["#16a34a", "#f59e0b", "#ef4444"],
        labels={value_col: "kg CO₂e", "label": ""},
        title=f"{label} – All Employees",
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        coloraxis_showscale=False,
        margin=dict(t=50, b=60),
        height=360,
    )
    fig.update_traces(
        text=display_df[value_col].round(2).astype(str) + " kg",
        textposition="outside"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Data table ───────────────────────────────────────────────────
    with st.expander("📋 Leaderboard Table"):
        table_df = df[["rank","name","department","eco_title", value_col,"coal_g"]].copy()
        table_df.columns = ["Rank","Name","Department","Title","Emission (kg CO₂e)","Coal Equiv. (g)"]
        st.dataframe(
            table_df.style.format({"Emission (kg CO₂e)": "{:.3f}", "Coal Equiv. (g)": "{:.1f}"})
                          .background_gradient(subset=["Emission (kg CO₂e)"], cmap="RdYlGn_r"),
            use_container_width=True,
            hide_index=True,
        )
