"""Shared Streamlit theme CSS for Reorg Case."""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@600;700&display=swap');

:root {
  --rc-blue: #0052FF;
  --rc-blue-hover: #0041CC;
  --rc-blue-soft: #E8F0FF;
  --rc-ink: #0F172A;
  --rc-ink-2: #1E293B;
  --rc-muted: #475569;
  --rc-border: #E2E8F0;
  --rc-surface: #F8FAFC;
  --rc-white: #FFFFFF;
  --rc-success: #047857;
  --rc-success-bg: #ECFDF5;
  --rc-warning: #B45309;
  --rc-warning-bg: #FFFBEB;
  --rc-danger: #B91C1C;
  --rc-danger-bg: #FEF2F2;
  --rc-info: #1D4ED8;
  --rc-info-bg: #EFF6FF;
  --rc-radius: 8px;
  --rc-input-bg: #0F172A;
  --rc-input-fg: #F8FAFC;
}

/* Base: light surface, dark body text. Avoid broad [class*="css"] color overrides. */
html, body, .stApp {
  font-family: "IBM Plex Sans", system-ui, sans-serif;
  color: var(--rc-ink) !important;
}

.stApp {
  background:
    radial-gradient(1200px 480px at 8% -10%, #E8F0FF 0%, transparent 55%),
    radial-gradient(900px 420px at 100% 0%, #F1F5F9 0%, transparent 50%),
    linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 42%, #F8FAFC 100%);
}

.block-container {
  padding-top: 1.25rem;
  padding-bottom: 3rem;
  max-width: 1180px;
}

/* Brand header */
.rc-brand {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.85rem;
  padding-bottom: 0.9rem;
  border-bottom: 1px solid var(--rc-border);
}
.rc-brand-name {
  font-family: "IBM Plex Serif", Georgia, serif !important;
  font-weight: 700;
  font-size: 2.05rem;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--rc-ink);
  margin: 0;
}
.rc-brand-name span {
  color: var(--rc-blue);
}
.rc-brand-tagline {
  margin: 0;
  color: var(--rc-muted);
  font-size: 0.95rem;
  font-weight: 400;
  max-width: 52rem;
  line-height: 1.45;
}

/* Stage framing */
.rc-stage {
  background: var(--rc-white);
  border: 1px solid var(--rc-border);
  border-left: 3px solid var(--rc-blue);
  border-radius: var(--rc-radius);
  padding: 0.85rem 1rem;
  margin: 0.35rem 0 1rem 0;
}
.rc-stage-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--rc-blue);
  margin: 0 0 0.25rem 0;
}
.rc-stage-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--rc-ink);
  margin: 0 0 0.3rem 0;
}
.rc-stage-help {
  margin: 0;
  color: var(--rc-muted);
  font-size: 0.9rem;
  line-height: 1.45;
}

/* Case status strip */
.rc-status-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
  background: var(--rc-white);
  border: 1px solid var(--rc-border);
  border-radius: var(--rc-radius);
  padding: 0.65rem 0.9rem;
  margin: 0.4rem 0 0.9rem 0;
}
.rc-status-id {
  font-size: 0.88rem;
  color: var(--rc-muted);
}
.rc-status-id code {
  font-size: 0.85rem;
  background: var(--rc-surface);
  border: 1px solid var(--rc-border);
  border-radius: 4px;
  padding: 0.1rem 0.4rem;
  color: var(--rc-ink-2);
}
.rc-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  padding: 0.22rem 0.55rem;
  border-radius: 5px;
  border: 1px solid transparent;
  white-space: nowrap;
}
.rc-badge::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}
.rc-badge-gray { background: #F1F5F9; color: #475569; border-color: #E2E8F0; }
.rc-badge-blue { background: var(--rc-blue-soft); color: var(--rc-blue); border-color: #C7D9FF; }
.rc-badge-orange { background: var(--rc-warning-bg); color: var(--rc-warning); border-color: #FDE68A; }
.rc-badge-green { background: var(--rc-success-bg); color: var(--rc-success); border-color: #A7F3D0; }
.rc-badge-red { background: var(--rc-danger-bg); color: var(--rc-danger); border-color: #FECACA; }

/* Callout cards */
.rc-callout {
  border-radius: var(--rc-radius);
  border: 1px solid var(--rc-border);
  padding: 0.75rem 0.9rem;
  margin: 0.4rem 0 0.65rem 0;
  background: var(--rc-white);
}
.rc-callout-title {
  font-weight: 600;
  font-size: 0.92rem;
  margin: 0 0 0.25rem 0;
  color: var(--rc-ink);
}
.rc-callout-body {
  margin: 0;
  font-size: 0.88rem;
  color: var(--rc-ink-2);
  line-height: 1.45;
}
.rc-callout-quote {
  margin: 0.45rem 0 0.35rem 0;
  padding: 0.45rem 0.65rem;
  border-left: 3px solid var(--rc-border);
  background: var(--rc-surface);
  color: var(--rc-muted);
  font-size: 0.85rem;
  font-style: italic;
}
.rc-callout-verified {
  border-left: 3px solid var(--rc-success);
  background: var(--rc-success-bg);
}
.rc-callout-unverified {
  border-left: 3px solid var(--rc-warning);
  background: var(--rc-warning-bg);
}
.rc-callout-required {
  border-left: 3px solid var(--rc-info);
  background: var(--rc-info-bg);
}
.rc-callout-granted {
  border-left: 3px solid var(--rc-success);
  background: var(--rc-success-bg);
}
.rc-pill {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 650;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.12rem 0.4rem;
  border-radius: 4px;
  margin-right: 0.35rem;
}
.rc-pill-ok { background: #D1FAE5; color: var(--rc-success); }
.rc-pill-warn { background: #FDE68A; color: #92400E; }
.rc-pill-req { background: #DBEAFE; color: var(--rc-info); }

/* Action rows */
.rc-action {
  border: 1px solid var(--rc-border);
  border-radius: var(--rc-radius);
  padding: 0.7rem 0.85rem;
  margin: 0.4rem 0;
  background: var(--rc-white);
}
.rc-action-top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.45rem 0.65rem;
  margin-bottom: 0.25rem;
}
.rc-action-id {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.78rem;
  color: var(--rc-muted);
  background: var(--rc-surface);
  border: 1px solid var(--rc-border);
  border-radius: 4px;
  padding: 0.08rem 0.35rem;
}
.rc-action-name {
  font-weight: 600;
  color: var(--rc-ink);
  font-size: 0.95rem;
}
.rc-type {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  padding: 0.12rem 0.4rem;
  border-radius: 4px;
}
.rc-type-auto { background: var(--rc-blue-soft); color: #003DB8; }
.rc-type-manual { background: #FEF3C7; color: #92400E; }
.rc-type-gate { background: #E2E8F0; color: #334155; }
.rc-action-meta {
  font-size: 0.82rem;
  color: var(--rc-muted);
  margin: 0.15rem 0;
}
.rc-action-desc {
  font-size: 0.88rem;
  color: var(--rc-ink-2);
  margin: 0.2rem 0 0 0;
}

/* Metrics polish */
div[data-testid="stMetric"] {
  background: var(--rc-white);
  border: 1px solid var(--rc-border);
  border-radius: var(--rc-radius);
  padding: 0.65rem 0.75rem;
}
div[data-testid="stMetricValue"] {
  font-size: 1.35rem !important;
  font-weight: 600 !important;
  color: var(--rc-ink) !important;
}
div[data-testid="stMetricLabel"] {
  color: var(--rc-muted) !important;
}

/* Buttons */
.stButton > button {
  border-radius: 7px !important;
  font-weight: 600 !important;
  font-family: "IBM Plex Sans", system-ui, sans-serif !important;
  border: 1px solid var(--rc-border) !important;
  color: var(--rc-ink) !important;
  background: var(--rc-white) !important;
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background: var(--rc-blue) !important;
  border-color: var(--rc-blue) !important;
  color: #fff !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
  background: var(--rc-blue-hover) !important;
  border-color: var(--rc-blue-hover) !important;
  box-shadow: 0 1px 3px rgba(0, 82, 255, 0.25);
}

/*
 * Tabs: Streamlit/BaseWeb dark-theme text can stay white while .stApp is forced light.
 * Pin inactive tabs to slate and active to brand blue.
 */
div[data-testid="stTabs"] [data-baseweb="tab-list"],
.stTabs [data-baseweb="tab-list"] {
  gap: 0.15rem;
  border-bottom: 1px solid var(--rc-border);
  background: transparent !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"],
.stTabs [data-baseweb="tab"],
div[data-testid="stTabs"] button[role="tab"],
.stTabs button[role="tab"] {
  font-weight: 500 !important;
  color: #334155 !important;
  padding: 0.55rem 0.85rem;
  font-family: "IBM Plex Sans", system-ui, sans-serif !important;
  background: transparent !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] p,
div[data-testid="stTabs"] button[role="tab"] p,
.stTabs button[role="tab"] p,
div[data-testid="stTabs"] [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] span,
div[data-testid="stTabs"] button[role="tab"] span,
.stTabs button[role="tab"] span {
  color: inherit !important;
}
div[data-testid="stTabs"] [aria-selected="true"],
.stTabs [aria-selected="true"],
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
.stTabs button[role="tab"][aria-selected="true"] {
  color: var(--rc-blue) !important;
  font-weight: 600 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-border"] {
  background-color: var(--rc-blue) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"],
.stTabs [data-baseweb="tab-panel"] {
  padding-top: 0.75rem;
}

/* Widget labels ABOVE inputs: always dark on light page */
label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] label,
.stTextArea label,
.stTextInput label,
.stSelectbox label,
.stCheckbox label,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li,
div[data-testid="stMarkdownContainer"] span,
.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
  color: var(--rc-ink) !important;
}
.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
  color: var(--rc-muted) !important;
}

/* Dark textarea with light text inside; labels stay dark above */
.stTextArea textarea,
div[data-testid="stTextArea"] textarea {
  background-color: var(--rc-input-bg) !important;
  color: var(--rc-input-fg) !important;
  border: 1px solid #1E293B !important;
  caret-color: var(--rc-input-fg) !important;
}
.stTextArea textarea::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
  color: #94A3B8 !important;
}

/* Regular text inputs stay light for readability */
.stTextInput input,
div[data-testid="stTextInput"] input {
  color: var(--rc-ink) !important;
  background-color: var(--rc-white) !important;
  border-color: var(--rc-border) !important;
}

/* Select / checkbox readable on light */
.stSelectbox [data-baseweb="select"] > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  color: var(--rc-ink) !important;
  background-color: var(--rc-white) !important;
}
.stCheckbox label span,
div[data-testid="stCheckbox"] label span {
  color: var(--rc-ink) !important;
}

/* Alerts / status callouts readable */
div[data-testid="stAlert"] {
  border-radius: var(--rc-radius);
}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div {
  color: inherit;
}

/* Sidebar text readable on light panel */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
  border-right: 1px solid var(--rc-border);
}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  color: var(--rc-ink) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
  font-family: "IBM Plex Sans", system-ui, sans-serif;
  color: var(--rc-ink) !important;
}
.rc-sidebar-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--rc-muted) !important;
  margin: 0 0 0.35rem 0;
}
.rc-sidebar-notes {
  font-size: 0.85rem;
  color: var(--rc-ink-2) !important;
  line-height: 1.45;
  background: var(--rc-surface);
  border: 1px solid var(--rc-border);
  border-radius: var(--rc-radius);
  padding: 0.65rem 0.75rem;
}

/* Hide default Streamlit chrome noise a bit */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
"""
