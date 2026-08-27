"""Demo-only session gate. No real authentication."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

# Demo credentials (documented in RUN.txt)
DEMO_USERNAME = "demouser"
DEMO_PASSWORD = "test123"

# Persist demo session across full page refresh.
# Query param is reliable on Streamlit Cloud; cookie is an optional local extra.
_AUTH_QUERY_KEY = "auth"
_AUTH_QUERY_VALUE = "demo"
_AUTH_COOKIE = "rw_demo_auth"
_AUTH_TOKEN = "rw-demo-v1"
_AUTH_MAX_AGE = 7 * 24 * 60 * 60  # 7 days

# Brand sits on the blue app background; the Streamlit form IS the white card.
# Never open a standalone HTML card around "Sign in" — widgets cannot nest in it.
LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

html, body, .stApp, .stApp * {
  font-family: "DM Sans", "Source Sans 3", system-ui, sans-serif !important;
}

.stApp {
  background:
    radial-gradient(900px 500px at 12% -5%, #1A4DFF 0%, transparent 55%),
    radial-gradient(700px 420px at 95% 10%, #0039B8 0%, transparent 50%),
    linear-gradient(165deg, #0033A0 0%, #0052FF 42%, #002B7A 100%) !important;
}

.block-container {
  padding-top: 1.35rem !important;
  padding-bottom: 1rem !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
  max-width: 400px !important;
  background: transparent !important;
}

/* Collapse Streamlit's default vertical rhythm on the login portal */
.block-container > div[data-testid="stVerticalBlock"] {
  gap: 0.4rem !important;
}
.block-container [data-testid="stMarkdownContainer"] {
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  text-align: center !important;
}
.block-container [data-testid="stMarkdownContainer"] p {
  margin: 0 !important;
  text-align: center !important;
}

/* Force brand markdown wrappers full-width + centered (Streamlit nests oddly) */
.block-container [data-testid="stElementContainer"]:has(.rw-portal-brand),
.block-container [data-testid="stMarkdown"]:has(.rw-portal-brand),
.block-container [data-testid="stMarkdownContainer"]:has(.rw-portal-brand),
.block-container [data-testid="stMarkdownContainer"]:has(.rw-portal-brand) > div,
.block-container [data-testid="stMarkdownContainer"]:has(.rw-portal-brand) p,
.block-container [data-testid="stMarkdownContainer"]:has(.rw-portal-brand) h1 {
  width: 100% !important;
  max-width: 100% !important;
  text-align: center !important;
  margin-left: auto !important;
  margin-right: auto !important;
  justify-content: center !important;
}

.rw-portal-brand {
  display: block !important;
  text-align: center !important;
  margin-left: auto !important;
  margin-right: auto !important;
  margin-top: 0 !important;
  margin-bottom: 0.5rem !important;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
}
.rw-portal-brand h1 {
  display: block !important;
  font-family: "DM Sans", "Source Sans 3", system-ui, sans-serif !important;
  font-weight: 700 !important;
  font-size: 1.85rem !important;
  line-height: 1.15 !important;
  color: #FFFFFF !important;
  margin: 0 auto 0.25rem auto !important;
  letter-spacing: -0.03em !important;
  text-align: center !important;
  width: 100% !important;
}
.rw-portal-brand h1 span { color: #B8D0FF !important; }
.rw-portal-brand p {
  display: block !important;
  margin: 0 auto !important;
  color: #D6E4FF !important;
  font-size: 0.88rem !important;
  line-height: 1.35 !important;
  text-align: center !important;
  font-weight: 400 !important;
  width: 100% !important;
  max-width: 22rem !important;
}

/* One cohesive white card = the form wrapping title + inputs + button */
div[data-testid="stForm"] {
  background: #FFFFFF !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.95rem 1.1rem 0.9rem 1.1rem !important;
  box-shadow: 0 14px 40px rgba(0, 16, 64, 0.32) !important;
  margin: 0 !important;
}
div[data-testid="stForm"] > div[data-testid="stVerticalBlock"] {
  gap: 0.4rem !important;
}
div[data-testid="stForm"] [data-testid="stElementContainer"],
div[data-testid="stForm"] [data-testid="stFormSubmitButton"],
div[data-testid="stForm"] div[data-testid="stTextInput"] {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}

/* Center "Sign in" inside the form card */
div[data-testid="stForm"] [data-testid="stElementContainer"]:has(.rw-login-card-title),
div[data-testid="stForm"] [data-testid="stMarkdown"]:has(.rw-login-card-title),
div[data-testid="stForm"] [data-testid="stMarkdownContainer"]:has(.rw-login-card-title),
div[data-testid="stForm"] [data-testid="stMarkdownContainer"]:has(.rw-login-card-title) p {
  text-align: center !important;
  width: 100% !important;
  margin-left: auto !important;
  margin-right: auto !important;
}
.rw-login-card-title {
  display: block !important;
  margin: 0 auto 0.15rem auto !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  color: #0F172A !important;
  font-family: "DM Sans", "Source Sans 3", system-ui, sans-serif !important;
  text-align: center !important;
  letter-spacing: -0.02em !important;
  width: 100% !important;
}

.rw-login-hint {
  display: block !important;
  margin: 0.65rem auto 0 auto !important;
  text-align: center !important;
  color: #C7D9FF !important;
  font-size: 0.78rem !important;
  line-height: 1.4 !important;
  width: 100% !important;
}

div[data-testid="stForm"] div[data-testid="stTextInput"] label p,
div[data-testid="stForm"] div[data-testid="stTextInput"] label span,
div[data-testid="stForm"] [data-testid="stWidgetLabel"] p {
  color: #1E293B !important;
  font-weight: 600 !important;
  text-align: left !important;
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

/*
  Hide the Streamlit show/hide password toggle. Global DM Sans font-family
  overrides break Material Icons ligatures ("visibility" renders as text).
  Password input remains type=password; toggle is optional for this demo.
*/
div[data-testid="stForm"] button[aria-label="Show password"],
div[data-testid="stForm"] button[aria-label="Hide password"],
div[data-testid="stForm"] [data-testid="stTextInput"] button[kind="icon"],
div[data-testid="stForm"] [data-testid="stTextInput"] button[data-testid="stBaseButton-icon"],
div[data-testid="stForm"] [data-testid="stTextInput"] button[data-testid="stBaseButton-secondary"],
div[data-testid="stForm"] [data-testid="InputInstruction"] {
  display: none !important;
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


def _set_auth_query_param() -> None:
    """Put demo auth in the URL so refresh keeps the session on Streamlit Cloud."""
    try:
        st.query_params[_AUTH_QUERY_KEY] = _AUTH_QUERY_VALUE
    except Exception:  # noqa: BLE001
        pass


def _clear_auth_query_param() -> None:
    try:
        if _AUTH_QUERY_KEY in st.query_params:
            del st.query_params[_AUTH_QUERY_KEY]
    except Exception:  # noqa: BLE001
        pass


def _query_auth_value() -> str | None:
    try:
        raw = st.query_params.get(_AUTH_QUERY_KEY)
    except Exception:  # noqa: BLE001
        return None
    if raw is None:
        return None
    if isinstance(raw, (list, tuple)):
        return str(raw[0]) if raw else None
    return str(raw)


def _mark_authenticated() -> None:
    st.session_state.authenticated = True
    st.session_state.auth_user = DEMO_USERNAME
    st.session_state.setdefault("view", "home")


def _restore_auth_from_query() -> bool:
    if _query_auth_value() != _AUTH_QUERY_VALUE:
        return False
    _mark_authenticated()
    return True


def _restore_auth_from_cookie() -> bool:
    try:
        token = st.context.cookies.get(_AUTH_COOKIE)
    except Exception:  # noqa: BLE001
        return False
    if token != _AUTH_TOKEN:
        return False
    _mark_authenticated()
    # Cookie worked locally — also mirror into the URL for Cloud-friendly refresh.
    _set_auth_query_param()
    return True


def is_authenticated() -> bool:
    if st.session_state.get("authenticated"):
        return True
    # Prefer query param (works on Streamlit Cloud); cookie is optional fallback.
    if _restore_auth_from_query():
        return True
    return _restore_auth_from_cookie()


def ensure_auth_cookie() -> None:
    """Keep demo auth persistence (query param + optional cookie) while signed in."""
    if not st.session_state.get("authenticated"):
        return
    if st.session_state.get("_auth_persist_written"):
        return
    _set_auth_query_param()
    _write_auth_cookie(_AUTH_TOKEN)
    st.session_state._auth_persist_written = True


def sign_out() -> None:
    st.session_state.authenticated = False
    st.session_state.pop("auth_user", None)
    st.session_state.pop("login_error", None)
    st.session_state.pop("_auth_persist_written", None)
    st.session_state.pop("_auth_cookie_written", None)
    st.session_state.view = "home"
    st.session_state.case = None
    _clear_auth_query_param()
    _write_auth_cookie("", max_age=0)


def render_login() -> None:
    """Portal login: brand on blue; one white form-card with all sign-in controls."""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="rw-portal-brand" style="text-align:center;width:100%;margin-left:auto;margin-right:auto;display:block;">
          <h1 style="text-align:center;width:100%;margin:0 auto 0.25rem auto;display:block;">Reorg <span>Workspace</span></h1>
          <p style="text-align:center;width:100%;margin:0 auto;display:block;max-width:22rem;">Governed reorganization cases for HR, Finance, and Ops</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        st.markdown(
            '<p class="rw-login-card-title" style="text-align:center;width:100%;margin:0 auto 0.15rem auto;display:block;">Sign in</p>',
            unsafe_allow_html=True,
        )
        username = st.text_input("Username", key="login_username", autocomplete="username")
        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
            autocomplete="current-password",
        )
        if st.session_state.get("login_error"):
            st.error(st.session_state.login_error)
        submitted = st.form_submit_button(
            "Sign in",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if username.strip() == DEMO_USERNAME and password == DEMO_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.auth_user = DEMO_USERNAME
            st.session_state.login_error = None
            st.session_state.view = "home"
            st.session_state.pop("_auth_persist_written", None)
            st.session_state.pop("_auth_cookie_written", None)
            _set_auth_query_param()
            _write_auth_cookie(_AUTH_TOKEN)
            st.rerun()
        else:
            st.session_state.login_error = (
                "Invalid username or password. Check RUN.txt for demo credentials."
            )
            st.rerun()

    st.markdown(
        '<p class="rw-login-hint" style="text-align:center;width:100%;margin:0.65rem auto 0 auto;display:block;">Demo credentials are in RUN.txt.</p>',
        unsafe_allow_html=True,
    )
