"""
app.py – Application entry point and router for the GHG Tracker.

Responsibilities:
  - Streamlit page config
  - CSS injection
  - Session state initialisation
  - Auth gate
  - Sidebar navigation
  - Page routing
"""

import streamlit as st
from database import init_db, get_user
from utils.styles import inject_css

# ── Page config (must be first Streamlit call) ────────────────────
st.set_page_config(
    page_title="GHG Tracker · CIL Sonpur Bazari",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Database init ─────────────────────────────────────────────────
init_db()

# ── Inject CSS ────────────────────────────────────────────────────
# inject_css()

# ── Session state defaults ────────────────────────────────────────
_defaults = {
    "page":        "login",
    "logged_in":   False,
    "employee_id": None,
    "user":        None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Auth gate ─────────────────────────────────────────────────────
def is_authenticated() -> bool:
    return st.session_state.get("logged_in", False)


# ── Sidebar navigation ─────────────────────────────────────────────
def render_sidebar():
    user = st.session_state.user
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="text-align:center; padding: 16px 0 24px;">
            <div style="font-size:40px">🌱</div>
            <div style="font-size:15px; font-weight:800; color:#86efac; letter-spacing:.04em;">
                GHG TRACKER
            </div>
            <div style="font-size:11px; color:#6ee7b7; margin-top:2px;">
                CIL Sonpur Bazari Area
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr style="border-color:rgba(34,197,94,.2)">', unsafe_allow_html=True)

        # User greeting
        st.markdown(f"""
        <div style="padding: 10px 4px 20px;">
            <div style="font-size:12px; color:#6ee7b7;">Logged in as</div>
            <div style="font-size:15px; font-weight:700; color:#ffffff; margin-top:2px;">
                {user['name']}
            </div>
            <div style="font-size:11px; color:#a7f3d0;">
                {user.get('department','–')} · {user['employee_id']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Nav items
        nav_items = [
            ("📅 Daily Log",   "daily_log"),
            ("🌱 Dashboard",   "dashboard"),
            ("🏆 Leaderboard", "leaderboard"),
            ("👤 My Profile",  "profile"),
        ]
        for label, page in nav_items:
            active = st.session_state.page == page
            btn_style = """
                background: rgba(34,197,94,.2) !important;
                color: #ffffff !important;
            """ if active else ""
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()

        st.markdown('<hr style="border-color:rgba(34,197,94,.2); margin-top:auto">', unsafe_allow_html=True)

        # World Environment Day footer
        st.markdown("""
        <div style="text-align:center; padding:12px 0; font-size:11px; color:#6ee7b7; line-height:1.6;">
            🌍 World Environment Day<br>
            <span style="opacity:.7;">Coal India Limited</span>
        </div>
        """, unsafe_allow_html=True)

        # Logout
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ── Main router ───────────────────────────────────────────────────
def main():
    if not is_authenticated():
        # Auth pages (no sidebar)
        if st.session_state.page == "register":
            from pages.auth import show_register
            show_register()
        else:
            from pages.auth import show_login
            show_login()
        return

    # Render sidebar for authenticated users
    render_sidebar()

    # Route to the correct page
    page = st.session_state.page

    if page == "daily_log":
        from pages.daily_log import show_daily_log
        show_daily_log()

    elif page == "dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()

    elif page == "leaderboard":
        from pages.leaderboard import show_leaderboard
        show_leaderboard()

    elif page == "profile":
        from pages.profile import show_profile
        show_profile()

    else:
        # Fallback
        st.session_state.page = "daily_log"
        st.rerun()


if __name__ == "__main__":
    main()
else:
    # When run via `streamlit run app.py`
    main()
