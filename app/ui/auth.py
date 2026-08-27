"""Demo-only session gate. No real authentication."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

# Demo credentials (documented in RUN.txt)
DEMO_USERNAME = "ops.demo"
DEMO_PASSWORD = "reorg-demo"

# Browser cookie so a full page refresh keeps the demo session.
_AUTH_COOKIE = "rw_demo_auth"
_AUTH_TOKEN = "rw-demo-v1-ops"
_AUTH_MAX_AGE = 7 * 24 * 60 * 60  # 7 days

# Brand sits on the blue app background; the form itself is the white card.
# (Streamlit cannot nest widgets inside an HTML <div>, so we never open a
# fake card wrapper around "Sign in" alone.)
LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@600;700&display=swap');

section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

html, body, .stApp {
  font-family: "IBM Plex Sans", system-ui, sans-serif !important;
}

.stApp {
  background:
    radial-gradient(900px 500px at 12% -5%, #1A4DFF 0%, transparent 55%),
    radial-gradient(700px 420px at 95% 10%, #0039B8 0%, transparent 50%),
    linear-gradient(165deg, #0033A0 0%, #0052FF 42%, #002B7A 100%) !important;
}

.block-container {
  padding-top: 4rem !important;
  padding-bottom: 2rem !important;
  max-width: 420px !important;
  background: transparent !important;
}

.rw-portal-brand {
  text-align: center;
  margin: 0 0 1.5rem 0;
}
.rw-portal-brand h1 {
  font-family: "IBM Plex Serif", Georgia, serif !important;
  font-weight: 700;
  font-size: 2.15rem;
  line-height: 1.15;
  color: #FFFFFF !important;
  margin: 0 0 0.45rem 0;
  letter-spacing: -0.02em;
}
.rw-portal-brand h1 span { color: #B8D0FF !important; }
.rw-portal-brand p {
  margin: 0;
  color: #D6E4FF !important;
  font-size: 0.95rem;
  line-height: 1.45;
}

/* One cohesive white card = the Streamlit form that wraps all login widgets */
div[data-testid="stForm"] {
  background: #FFFFFF !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 1.6rem 1.45rem 1.35rem 1.45rem !important;
  box-shadow: 0 16px 48px rgba(0, 16, 64, 0.35) !important;
}

.rw-login-card-title {
  margin: 0 0 1.05rem 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #0F172A !important;
  font-family: "IBM Plex Sans", system-ui, sans-serif !important;
}

.rw-login-hint {
  margin: 1rem 0 0 0;
  text-align: center;
  color: #C7D9FF !important;
  font-size: 0.78rem;
  line-height: 1.4;
}

div[data-testid="stForm"] div[data-testid="stTextInput"] label p,
div[data-testid="stForm"] div[data-testid="stTextInput"] label span,
div[data-testid="stForm"] [data-testid="stWidgetLabel"] p {
  color: #1E293B !important;
  font-weight: 600 !important;
}
div[data-testid="stForm"] div[data-testid="stTextInput"] input {
  background: #F8FAFC !important;
  color: #0B1220 !important;
  border: 1px solid #94A3B8 !important;
  border-radius: 8px !important;
}

div[data-testid="stForm"] .stButton > button,
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"],
div[data-testid="stForm"] button[kind="primary"],
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
  background: #0052FF !important;
  color: #FFFFFF !important;
  border: 1px solid #0052FF !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
  width: 100%;
}
div[data-testid="stForm"] .stButton > button:hover,
div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:hover,
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
  background: #0041CC !important;
  border-color: #0041CC !important;
  color: #FFFFFF !important;
}

div[data-testid="stAlert"] { border-radius: 8px; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.stDeployButton, [data-testid="stDeployButton"],
div[data-testid="stToolbar"] button[kind="header"],
div[data-testid="stToolbar"] a { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
</style>
"""


def _write_auth_cookie(token: str, *, max_age: int = _AUTH_MAX_AGE) -> None:
    """Set or clear a browser cookie. Streamlit can read cookies but not write them."""
    components.html(
        f"""
        <script>
        document.cookie = "{_AUTH_COOKIE}={token}; path=/; max-age={max_age}; SameSite=Lax";
        </script>
        """,
        height=0,
        width=0,
    )


def _restore_auth_from_cookie() -> bool:
    try:
        token = st.context.cookies.get(_AUTH_COOKIE)
    except Exception:  # noqa: BLE001
        return False
    if token != _AUTH_TOKEN:
        return False
    st.session_state.authenticated = True
    st.session_state.auth_user = DEMO_USERNAME
    st.session_state.setdefault("view", "home")
    return True


def is_authenticated() -> bool:
    if st.session_state.get("authenticated"):
        return True
    return _restore_auth_from_cookie()


def ensure_auth_cookie() -> None:
    """Keep the demo auth cookie fresh while the user is signed in."""
    if not st.session_state.get("authenticated"):
        return
    if st.session_state.get("_auth_cookie_written"):
        return
    _write_auth_cookie(_AUTH_TOKEN)
    st.session_state._auth_cookie_written = True


def sign_out() -> None:
    st.session_state.authenticated = False
    st.session_state.pop("auth_user", None)
    st.session_state.pop("login_error", None)
    st.session_state.pop("_auth_cookie_written", None)
    st.session_state.view = "home"
    st.session_state.case = None
    _write_auth_cookie("", max_age=0)


def render_login() -> None:
    """Portal login: brand on blue, one white form-card with all sign-in controls."""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="rw-portal-brand">
          <h1>Reorg <span>Workspace</span></h1>
          <p>Governed reorganization cases for HR, Finance, and Ops</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        st.markdown(
            '<p class="rw-login-card-title">Sign in</p>',
            unsafe_allow_html=True,
        )
        username = st.text_input("Username", key="login_username", autocomplete="username")
        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
            autocomplete="current-password",
        )
        submitted = st.form_submit_button(
            "Sign in",
            type="primary",
            use_container_width=True,
        )

    if st.session_state.get("login_error"):
        st.error(st.session_state.login_error)

    if submitted:
        if username.strip() == DEMO_USERNAME and password == DEMO_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.auth_user = DEMO_USERNAME
            st.session_state.login_error = None
            st.session_state.view = "home"
            st.session_state.pop("_auth_cookie_written", None)
            _write_auth_cookie(_AUTH_TOKEN)
            st.rerun()
        else:
            st.session_state.login_error = (
                "Invalid username or password. Check RUN.txt for demo credentials."
            )
            st.rerun()

    st.markdown(
        '<p class="rw-login-hint">Demo credentials are in RUN.txt.</p>',
        unsafe_allow_html=True,
    )
