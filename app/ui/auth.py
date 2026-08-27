"""Demo-only session gate. No real authentication."""

from __future__ import annotations

import streamlit as st

# Demo credentials (documented in RUN.txt)
DEMO_USERNAME = "ops.demo"
DEMO_PASSWORD = "reorg-demo"

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
  padding-top: 4.5rem !important;
  max-width: 420px !important;
}

.rc-login-card {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 12px;
  padding: 1.75rem 1.5rem 1.35rem 1.5rem;
  backdrop-filter: blur(8px);
  box-shadow: 0 12px 40px rgba(0, 20, 80, 0.35);
}
.rc-login-brand {
  font-family: "IBM Plex Serif", Georgia, serif !important;
  font-weight: 700;
  font-size: 1.85rem;
  line-height: 1.15;
  color: #FFFFFF !important;
  margin: 0 0 0.35rem 0;
  letter-spacing: -0.02em;
}
.rc-login-brand span { color: #B8D0FF !important; }
.rc-login-sub {
  margin: 0 0 1.15rem 0;
  color: #E8F0FF !important;
  font-size: 0.92rem;
  line-height: 1.45;
  font-weight: 400;
}
.rc-login-hint {
  margin: 0.85rem 0 0 0;
  color: #C7D9FF !important;
  font-size: 0.78rem;
  line-height: 1.4;
}

/* High-contrast form chrome on blue */
div[data-testid="stTextInput"] label p,
div[data-testid="stTextInput"] label span,
[data-testid="stWidgetLabel"] p {
  color: #FFFFFF !important;
  font-weight: 600 !important;
}
div[data-testid="stTextInput"] input {
  background: #FFFFFF !important;
  color: #0B1220 !important;
  border: 1px solid rgba(255, 255, 255, 0.55) !important;
  border-radius: 8px !important;
}
div[data-testid="stTextInput"] input::placeholder {
  color: #64748B !important;
}

.stButton > button {
  background: #FFFFFF !important;
  color: #0033A0 !important;
  border: 1px solid #FFFFFF !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
  width: 100%;
}
.stButton > button:hover {
  background: #E8F0FF !important;
  color: #002B7A !important;
  border-color: #E8F0FF !important;
}

div[data-testid="stAlert"] {
  border-radius: 8px;
}

/* Minimize Streamlit chrome / hide Deploy */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.stDeployButton, [data-testid="stDeployButton"],
div[data-testid="stToolbar"] button[kind="header"],
div[data-testid="stToolbar"] a { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
</style>
"""


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated"))


def sign_out() -> None:
    st.session_state.authenticated = False
    st.session_state.pop("auth_user", None)
    st.session_state.pop("login_error", None)


def render_login() -> None:
    """Full-bleed blue login gate. Mutates session_state on success."""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="rc-login-card">
          <p class="rc-login-brand">Reorg <span>Case</span></p>
          <p class="rc-login-sub">Sign in</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")  # spacing
    username = st.text_input("Username", key="login_username", autocomplete="username")
    password = st.text_input(
        "Password",
        type="password",
        key="login_password",
        autocomplete="current-password",
    )

    if st.session_state.get("login_error"):
        st.error(st.session_state.login_error)

    if st.button("Sign in", type="primary", use_container_width=True):
        if username.strip() == DEMO_USERNAME and password == DEMO_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.auth_user = DEMO_USERNAME
            st.session_state.login_error = None
            st.rerun()
        else:
            st.session_state.login_error = (
                "Invalid username or password. Check RUN.txt for demo credentials."
            )
            st.rerun()

    st.markdown(
        '<p class="rc-login-hint">Demo credentials are in RUN.txt.</p>',
        unsafe_allow_html=True,
    )
