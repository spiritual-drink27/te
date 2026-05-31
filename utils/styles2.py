"""
utils/styles.py – Central CSS injection for the GHG Tracker app.
"""

import streamlit as st


def inject_css1():
    st.markdown("""
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ── Root Variables ── */
    :root {
        --green-950: #052e16;
        --green-900: #14532d;
        --green-800: #166534;
        --green-700: #15803d;
        --green-600: #16a34a;
        --green-500: #22c55e;
        --green-400: #4ade80;
        --green-300: #86efac;
        --green-100: #dcfce7;
        --green-50:  #f0fdf4;
        --amber:     #f59e0b;
        --red:       #ef4444;
        --slate-900: #0f172a;
        --slate-800: #1e293b;
        --slate-700: #334155;
        --slate-200: #e2e8f0;
        --slate-100: #f1f5f9;
        --radius:    12px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
        --shadow:    0 4px 16px rgba(0,0,0,.08), 0 2px 6px rgba(0,0,0,.04);
        --shadow-lg: 0 10px 40px rgba(0,0,0,.12), 0 4px 12px rgba(0,0,0,.06);
    }

    /* ── Global reset ── */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background: #f8fdf9 !important;
        color: #1a2e1a !important;
    }

    /* ── Hide Streamlit chrome ── */
    /* Header, footer, main menu */
    #MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }

    /* Hide Streamlit's auto-generated multipage navigation in sidebar
       (the list of pages that appears when you have a pages/ folder) 
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebarNavItems"] { display: none !important; }
    [data-testid="stSidebarNavSeparator"] { display: none !important; } */

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #052e16 0%, #0a4522 60%, #14532d 100%) !important;
        border-right: 1px solid rgba(34,197,94,.15);
    }
    [data-testid="stSidebar"] * { color: #d1fae5 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #86efac !important; }

    /* Sidebar nav buttons – base style */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left !important;
        justify-content: flex-start !important;
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        color: #a7f3d0 !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(34,197,94,.15) !important;
        color: #ffffff !important;
        transform: translateX(3px) !important;
    }

    /* Active nav button – targets the button marked active via data attribute */
    [data-testid="stSidebar"] .stButton > button[data-active="true"],
    [data-testid="stSidebar"] .nav-active > button {
        background: rgba(34,197,94,.25) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-left: 3px solid #4ade80 !important;
    }

    /* ── Top app bar / page header ── */
    .ghg-header {
        background: linear-gradient(135deg, #052e16 0%, #166534 50%, #15803d 100%);
        border-radius: var(--radius);
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--shadow-lg);
    }
    .ghg-header h1 {
        color: #ffffff !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .ghg-header .subtitle {
        color: #86efac;
        font-size: 13px;
        margin-top: 2px;
    }

    /* ── Cards ── */
    .metric-card {
        background: #ffffff;
        border-radius: var(--radius);
        padding: 20px 22px;
        border: 1px solid #e7f5eb;
        box-shadow: var(--shadow-sm);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow);
    }
    .metric-card .label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: #6b7280;
        margin-bottom: 6px;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: 800;
        color: #052e16;
        line-height: 1;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-card .unit {
        font-size: 13px;
        font-weight: 500;
        color: #6b7280;
        margin-top: 2px;
    }
    .metric-card .icon {
        font-size: 28px;
        margin-bottom: 8px;
        display: block;
    }

    /* Colored accent bar */
    .metric-card.green  { border-top: 4px solid #22c55e; }
    .metric-card.teal   { border-top: 4px solid #14b8a6; }
    .metric-card.blue   { border-top: 4px solid #3b82f6; }
    .metric-card.amber  { border-top: 4px solid #f59e0b; }
    .metric-card.red    { border-top: 4px solid #ef4444; }
    .metric-card.purple { border-top: 4px solid #8b5cf6; }
    .metric-card.stone  { border-top: 4px solid #78716c; }

    /* ── Eco Title Badge ── */
    .eco-badge {
        border-radius: 999px;
        padding: 6px 18px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        letter-spacing: .04em;
    }

    /* ── Equivalents card ── */
    .equiv-card {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border-radius: var(--radius);
        padding: 16px 18px;
        border: 1px solid #bbf7d0;
        text-align: center;
    }
    .equiv-card .eq-icon { font-size: 28px; }
    .equiv-card .eq-val  { font-size: 22px; font-weight: 800; color: #14532d; font-family: 'JetBrains Mono', monospace; }
    .equiv-card .eq-lbl  { font-size: 11px; color: #166534; font-weight: 600; text-transform: uppercase; letter-spacing: .07em; }

    /* ── Leaderboard ── */
    .lb-row {
        background: #ffffff;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 14px;
        border: 1px solid #e7f5eb;
        box-shadow: var(--shadow-sm);
    }
    .lb-row.gold   { border-left: 4px solid #f59e0b; background: #fffbeb; }
    .lb-row.silver { border-left: 4px solid #94a3b8; background: #f8fafc; }
    .lb-row.bronze { border-left: 4px solid #ca8a04; background: #fefce8; }
    .lb-rank { font-size: 20px; font-weight: 800; min-width: 32px; color: #374151; font-family: 'JetBrains Mono', monospace; }
    .lb-name { font-weight: 700; font-size: 15px; color: #111827; }
    .lb-dept { font-size: 12px; color: #6b7280; }
    .lb-val  { margin-left: auto; font-weight: 800; font-size: 18px; font-family: 'JetBrains Mono', monospace; color: #15803d; }
    .lb-unit { font-size: 11px; color: #6b7280; }

    /* ── Profile info grid ── */
    .profile-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .profile-item {
        background: rgba(34,197,94,.06);
        border-radius: 8px;
        padding: 10px 14px;
        border: 1px solid rgba(34,197,94,.15);
    }
    .profile-item .pi-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #6b7280; }
    .profile-item .pi-val   { font-size: 14px; font-weight: 600; color: #052e16; margin-top: 2px; }

    /* ── Forms: labels ── */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stDateInput > label {
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #374151 !important;
    }

    /* ── Forms: input boxes – WHITE background so text is always visible ── */
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input {
        border-radius: 8px !important;
        border: 1.5px solid #bbf7d0 !important;
        background: #ffffff !important;
        color: #111827 !important;
        font-size: 14px !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus {
        border-color: #22c55e !important;
        box-shadow: 0 0 0 3px rgba(34,197,94,.12) !important;
        background: #ffffff !important;
        color: #111827 !important;
    }
    /* Placeholder text */
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {
        color: #9ca3af !important;
    }
    /* Number input spinner buttons */
    .stNumberInput [data-baseweb="input"] {
        background: #ffffff !important;
    }
    /* Selectbox */
    .stSelectbox [data-baseweb="select"] > div {
        border-radius: 8px !important;
        border: 1.5px solid #bbf7d0 !important;
        background: #ffffff !important;
        color: #111827 !important;
    }
    /* Date picker */
    .stDateInput [data-baseweb="input"] > div {
        background: #ffffff !important;
        color: #111827 !important;
    }

    /* Primary / submit buttons */
    .stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #15803d, #16a34a) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(21,128,61,.3) !important;
        letter-spacing: .03em;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(21,128,61,.4) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #f0fdf4 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1px solid #bbf7d0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #15803d !important;
    }
    .stTabs [aria-selected="true"] {
        background: #15803d !important;
        color: white !important;
    }

    /* ── Success/info alerts ── */
    .stAlert { border-radius: 10px !important; }

    /* ── Section headers ── */
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #052e16;
        margin: 24px 0 14px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, #bbf7d0, transparent);
        margin-left: 12px;
    }

    /* ── Login page ── */
    .login-wrap {
        max-width: 440px;
        margin: 60px auto 0;
        background: white;
        border-radius: 20px;
        padding: 48px 40px;
        box-shadow: var(--shadow-lg);
        border: 1px solid #e7f5eb;
    }
    .login-logo { font-size: 48px; text-align: center; margin-bottom: 12px; }
    .login-title {
        font-size: 26px; font-weight: 800; color: #052e16;
        text-align: center; margin-bottom: 4px;
    }
    .login-sub {
        font-size: 13px; color: #6b7280;
        text-align: center; margin-bottom: 32px;
    }

    /* ── Streak badge ── */
    .streak-badge {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        border-radius: 999px;
        padding: 4px 14px;
        font-size: 12px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    /* ── Divider ── */
    .ghg-divider {
        border: none;
        border-top: 1px solid #d1fae5;
        margin: 20px 0;
    }

    /* ── Active sidebar nav item (CSS class injected via st.markdown) ── */
    .nav-btn-active > div > button {
        background: rgba(34,197,94,.25) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-left: 3px solid #4ade80 !important;
    }
    </style>
    """, unsafe_allow_html=True)
