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
  --rc-input-bg: #F1F5F9;
  --rc-input-fg: #0F172A;
  --rc-input-border: #64748B;
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
  padding-top: 1rem;
  padding-bottom: 2.5rem;
  max-width: 1180px;
}

/* Brand header */
.rc-brand {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin: 0 0 0.55rem 0;
  padding: 0 0 0.55rem 0;
  border-bottom: 1px solid var(--rc-border);
}
.rc-brand-name {
  font-family: "IBM Plex Serif", Georgia, serif !important;
  font-weight: 700;
  font-size: 1.85rem;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--rc-ink);
  margin: 0 0 0.15rem 0;
}
.rc-brand-name span {
  color: var(--rc-blue);
}
.rc-brand-tagline {
  margin: 0;
  color: var(--rc-muted);
  font-size: 0.9rem;
  font-weight: 400;
  max-width: 52rem;
  line-height: 1.4;
}

/* Home workspace: tighter Streamlit rhythm + aligned past-case rows */
.rc-home-root { display: none; }
.block-container:has(.rc-home-root) {
  padding-top: 0.85rem !important;
}
/* Center home brand + tagline (case view keeps left-aligned brand) */
.block-container:has(.rc-home-root) .rc-brand {
  align-items: center !important;
  text-align: center !important;
  width: 100% !important;
}
.block-container:has(.rc-home-root) .rc-brand-name,
.block-container:has(.rc-home-root) .rc-brand-tagline {
  text-align: center !important;
  margin-left: auto !important;
  margin-right: auto !important;
  max-width: 40rem;
}
.block-container:has(.rc-home-root) [data-testid="stElementContainer"]:has(.rc-brand),
.block-container:has(.rc-home-root) [data-testid="stMarkdown"]:has(.rc-brand),
.block-container:has(.rc-home-root) [data-testid="stMarkdownContainer"]:has(.rc-brand),
.block-container:has(.rc-home-root) [data-testid="stMarkdownContainer"]:has(.rc-brand) > div {
  width: 100% !important;
  max-width: 100% !important;
  text-align: center !important;
  display: block !important;
}
.block-container:has(.rc-home-root) > div[data-testid="stVerticalBlock"] {
  gap: 0.7rem !important;
}
.block-container:has(.rc-home-root) [data-testid="stHorizontalBlock"] {
  gap: 1.1rem !important;
  align-items: flex-start !important;
}
/* Column rhythm: keep readable space between copy and actions */
.block-container:has(.rc-home-root) [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
  gap: 0.75rem !important;
}
/* Zero margins on non-button home elements only — never collapse action spacing */
.block-container:has(.rc-home-root) [data-testid="stElementContainer"]:not(:has(.stButton)):not(:has(.rc-home-lead)) {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}
/* Clear gap above home column buttons (fixes overlap covering description text) */
.block-container:has(.rc-home-root) [data-testid="stColumn"] [data-testid="stElementContainer"]:has(.stButton) {
  margin-top: 0.75rem !important;
  margin-bottom: 0 !important;
  padding-top: 0.2rem !important;
}
.block-container:has(.rc-home-root) [data-testid="stColumn"] .stButton,
.block-container:has(.rc-home-root) [data-testid="stColumn"] .stButton > button {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  position: relative !important;
  top: 0 !important;
  transform: none !important;
}
.block-container:has(.rc-home-root) [data-testid="stMarkdownContainer"] h3 {
  margin: 0 0 0.55rem 0 !important;
  font-size: 1.02rem !important;
  font-weight: 600 !important;
  line-height: 1.25 !important;
  color: var(--rc-ink) !important;
}
.block-container:has(.rc-home-root) [data-testid="stMarkdownContainer"] p {
  margin: 0 !important;
  line-height: 1.45 !important;
}
/* Lead copy under New Reorg Case — padding keeps button clear of text */
.rc-home-lead {
  display: block !important;
  margin: 0 0 0.35rem 0 !important;
  padding: 0 0 0.55rem 0 !important;
  line-height: 1.45 !important;
  color: var(--rc-ink) !important;
  font-size: 1rem !important;
}
.block-container:has(.rc-home-root) [data-testid="stElementContainer"]:has(.rc-home-lead) {
  margin-bottom: 0.15rem !important;
  overflow: visible !important;
}
.block-container:has(.rc-home-root) [data-testid="stCaptionContainer"] {
  margin: 0 !important;
  padding: 0 !important;
}
.block-container:has(.rc-home-root) [data-testid="stCaptionContainer"] p {
  margin: 0 !important;
  line-height: 1.35 !important;
}
.rc-home-section-label {
  margin: 0 0 0.35rem 0;
  padding-top: 0;
  border-top: none;
  font-size: 1.02rem;
  font-weight: 600;
  color: var(--rc-ink);
  line-height: 1.25;
}
/* Soft section cards (New Reorg Case / Quick load / Past cases) */
.block-container:has(.rc-home-root) div[data-testid="stVerticalBlockBorderWrapper"] {
  background: #F8FAFC !important;
  border: 1px solid var(--rc-border) !important;
  border-radius: 10px !important;
  padding: 0.85rem 1rem 1rem 1rem !important;
  box-shadow: none !important;
}
.block-container:has(.rc-home-root) div[data-testid="stVerticalBlockBorderWrapper"] > div {
  gap: 0.65rem !important;
}
.rc-past-cases-root {
  display: none;
}

/*
 * Past cases: every row (and the Status/Action header) is a Streamlit
 * horizontal block with the same column weights. Target by content markers
 * so New Reorg Case / Quick load columns are untouched.
 */
[data-testid="stHorizontalBlock"]:has(.rc-case-main),
[data-testid="stHorizontalBlock"]:has(.rc-case-col-head) {
  gap: 0.75rem !important;
  align-items: start !important;
  box-sizing: border-box !important;
  width: 100% !important;
  max-width: 100% !important;
  /* Counter parent vertical-block gap so rows read as one list. */
  margin: -0.22rem 0 !important;
  padding: 0.62rem 0 !important;
  border-bottom: 1px solid var(--rc-border);
  overflow-x: clip;
}
/*
 * Status / Action labels must sit cleanly ABOVE the list divider.
 * The shared rule's overflow-x:clip can collapse row height below the
 * label text so border-bottom cuts through "Status"/"Action". Override
 * overflow, give the header a real min-height, and pad below the labels
 * before the divider.
 */
[data-testid="stHorizontalBlock"]:has(.rc-case-col-head) {
  border-bottom: 1px solid var(--rc-border) !important;
  padding: 0.2rem 0 0.55rem 0 !important;
  margin: 0.15rem 0 0.45rem 0 !important;
  min-height: 1.85rem !important;
  overflow: visible !important;
  align-items: center !important;
}
/* No trailing divider after the last case. */
[data-testid="stHorizontalBlock"]:has(.rc-case-row-last) {
  border-bottom: none;
}
[data-testid="stHorizontalBlock"]:has(.rc-case-main) > div[data-testid="stColumn"],
[data-testid="stHorizontalBlock"]:has(.rc-case-col-head) > div[data-testid="stColumn"] {
  box-sizing: border-box !important;
  min-width: 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.rc-case-main)
  > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"]:has(.rc-case-col-head)
  > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
}
/* Open buttons: no extra top margin (home CTAs keep 0.75rem above). */
[data-testid="stHorizontalBlock"]:has(.rc-case-main)
  [data-testid="stElementContainer"]:has(.stButton) {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  padding-top: 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.rc-case-main) .stButton > button {
  min-height: 2rem !important;
  padding-top: 0.28rem !important;
  padding-bottom: 0.28rem !important;
  font-size: 0.82rem !important;
}
.rc-case-col-head {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--rc-muted);
  line-height: 1.25;
  padding: 0;
  display: block;
}
.rc-case-col-head-action {
  text-align: right;
}
/* Keep the empty Case column from collapsing header row metrics. */
.rc-case-col-spacer {
  display: block;
  width: 100%;
  height: 1.1rem;
  visibility: hidden;
  pointer-events: none;
}
.rc-case-main {
  display: flex;
  flex-direction: column;
  gap: 0.22rem;
  min-width: 0;
  box-sizing: border-box;
  max-width: 100%;
}
.rc-case-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--rc-ink);
  line-height: 1.35;
}
.rc-case-meta {
  margin: 0;
  font-size: 0.8rem;
  color: var(--rc-muted);
  line-height: 1.4;
}
.rc-case-note {
  margin: 0.12rem 0 0 0;
  font-size: 0.8rem;
  color: var(--rc-ink-2);
  line-height: 1.4;
}
.rc-case-status {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  padding-top: 0.18rem;
  box-sizing: border-box;
  max-width: 100%;
}
.rc-case-action {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  padding-top: 0.38rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--rc-muted);
  box-sizing: border-box;
  max-width: 100%;
}
@media (max-width: 720px) {
  [data-testid="stHorizontalBlock"]:has(.rc-case-main) {
    gap: 0.45rem !important;
    padding: 0.55rem 0 !important;
  }
  [data-testid="stHorizontalBlock"]:has(.rc-case-col-head) {
    gap: 0.45rem !important;
    border-bottom: 1px solid var(--rc-border) !important;
    padding: 0.15rem 0 0.5rem 0 !important;
    margin: 0.1rem 0 0.3rem 0 !important;
    min-height: 1.7rem !important;
    overflow: visible !important;
  }
  .rc-case-col-head-action {
    text-align: left;
  }
  .rc-case-action {
    justify-content: flex-start;
  }
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

/* Buttons: secondary/outline always readable on white (not white-on-white) */
.stButton > button {
  border-radius: 7px !important;
  font-weight: 600 !important;
  font-family: "IBM Plex Sans", system-ui, sans-serif !important;
  border: 1.5px solid #64748B !important;
  color: var(--rc-ink) !important;
  background: var(--rc-surface) !important;
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover {
  background: var(--rc-blue-soft) !important;
  border-color: var(--rc-blue) !important;
  color: var(--rc-ink) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background: var(--rc-blue) !important;
  border-color: var(--rc-blue) !important;
  color: #FFFFFF !important;
}
/* Nested label nodes inherit app ink unless forced white */
.stButton > button[kind="primary"] *,
.stButton > button[data-testid="baseButton-primary"] * {
  color: #FFFFFF !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
  background: var(--rc-blue-hover) !important;
  border-color: var(--rc-blue-hover) !important;
  color: #FFFFFF !important;
  box-shadow: 0 1px 3px rgba(0, 82, 255, 0.25);
}
.stButton > button[kind="primary"]:hover *,
.stButton > button[data-testid="baseButton-primary"]:hover * {
  color: #FFFFFF !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
section[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] * {
  color: #FFFFFF !important;
}

/* Sidebar buttons: white / soft-blue outlines on login blue */
section[data-testid="stSidebar"] .stButton > button {
  background: rgba(255, 255, 255, 0.12) !important;
  border: 1.5px solid rgba(255, 255, 255, 0.72) !important;
  color: #FFFFFF !important;
  box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button *,
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {
  color: #FFFFFF !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(232, 240, 255, 0.95) !important;
  border-color: #FFFFFF !important;
  color: #0033A0 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover *,
section[data-testid="stSidebar"] .stButton > button:hover p,
section[data-testid="stSidebar"] .stButton > button:hover span {
  color: #0033A0 !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
  background: #FFFFFF !important;
  border-color: #FFFFFF !important;
  color: #0033A0 !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
section[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] * {
  color: #0033A0 !important;
}

/*
 * Tabs (Streamlit 1.6x uses React Aria: [data-testid="stTab"] / role=tab).
 * Pin inactive tabs to slate and active to brand blue. Override any dark-theme
 * white text and do not let the global markdown ink rule win inside tabs.
 */
div[data-testid="stTabs"] [role="tablist"] {
  gap: 0.15rem;
  border-bottom: 1px solid var(--rc-border);
  background: transparent !important;
}
div[data-testid="stTabs"] [data-testid="stTab"],
div[data-testid="stTabs"] [role="tab"] {
  font-weight: 600 !important;
  color: #0F172A !important;
  opacity: 1 !important;
  padding: 0.55rem 0.85rem;
  font-family: "IBM Plex Sans", system-ui, sans-serif !important;
  background: transparent !important;
}
div[data-testid="stTabs"] [data-testid="stTab"] p,
div[data-testid="stTabs"] [role="tab"] p,
div[data-testid="stTabs"] [data-testid="stTab"] span,
div[data-testid="stTabs"] [role="tab"] span,
div[data-testid="stTabs"] [data-testid="stTab"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stTabs"] [role="tab"] [data-testid="stMarkdownContainer"] p {
  color: #0F172A !important;
  opacity: 1 !important;
  font-weight: 600 !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
  color: var(--rc-blue) !important;
  font-weight: 700 !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] p,
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] span,
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] span,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p {
  color: var(--rc-blue) !important;
  font-weight: 700 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] {
  background-color: var(--rc-blue) !important;
}
div[data-testid="stTabs"] [role="tabpanel"] {
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
.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
  color: var(--rc-ink) !important;
  opacity: 1 !important;
}
/* Body markdown (exclude tab labels, which are also stMarkdownContainer) */
.stApp .block-container > div div[data-testid="stMarkdownContainer"] p,
.stApp .block-container > div div[data-testid="stMarkdownContainer"] li {
  color: var(--rc-ink);
}
.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
  color: var(--rc-muted) !important;
}

/*
 * Freeform textarea: subtle fill + clear border so it reads as an input
 * on the white page (Streamlit default can blend into .stApp).
 */
div[data-testid="stTextArea"],
.stTextArea {
  background: transparent !important;
}
div[data-testid="stTextArea"] > div,
.stTextArea > div {
  border-radius: var(--rc-radius) !important;
}
.stTextArea textarea,
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextArea"] [data-baseweb="textarea"],
div[data-testid="stTextArea"] [data-baseweb="base-input"] {
  background-color: var(--rc-input-bg) !important;
  color: var(--rc-input-fg) !important;
  border: 1.5px solid var(--rc-input-border) !important;
  border-radius: var(--rc-radius) !important;
  caret-color: var(--rc-input-fg) !important;
  box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.06) !important;
}
.stTextArea textarea:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--rc-blue) !important;
  box-shadow: 0 0 0 2px rgba(0, 82, 255, 0.18) !important;
}
.stTextArea textarea::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
  color: #64748B !important;
}

/* Regular text inputs stay light for readability */
.stTextInput input,
div[data-testid="stTextInput"] input {
  color: var(--rc-ink) !important;
  background-color: var(--rc-white) !important;
  border-color: var(--rc-border) !important;
}

/* Select / checkbox readable on light (main canvas) */
.stSelectbox [data-baseweb="select"] > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  color: var(--rc-ink) !important;
  background-color: #E8EEF6 !important;
  border-color: #94A3B8 !important;
}
.stSelectbox [data-baseweb="select"] > div:hover,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
  background-color: var(--rc-blue-soft) !important;
  border-color: var(--rc-blue) !important;
}
.stCheckbox label span,
div[data-testid="stCheckbox"] label span {
  color: var(--rc-ink) !important;
}

/* Home Quick load: scenario notes preview under selectbox */
.rc-scenario-preview {
  margin: 0.15rem 0 0.1rem 0;
  padding: 0.55rem 0.7rem;
  background: var(--rc-surface);
  border: 1px solid var(--rc-border);
  border-left: 3px solid var(--rc-blue);
  border-radius: var(--rc-radius);
}
.rc-scenario-preview-label {
  margin: 0 0 0.2rem 0 !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--rc-muted) !important;
  line-height: 1.3 !important;
}
.rc-scenario-preview-body {
  margin: 0 !important;
  font-size: 0.84rem !important;
  color: var(--rc-ink-2) !important;
  line-height: 1.45 !important;
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

/*
 * Sidebar chrome = one solid brand blue (#0052FF / --rc-blue).
 * Do NOT use a multi-stop gradient here: sticky stSidebarHeader is a
 * separate opaque layer, and any gradient vs solid mismatch shows as a
 * horizontal band under the collapse strip.
 */
section[data-testid="stSidebar"] {
  background: #0052FF !important;
  background-image: none !important;
  border-right: 1px solid rgba(0, 43, 122, 0.55);
}
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarNav"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
  background: transparent !important;
  background-image: none !important;
  background-color: transparent !important;
}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
  color: #E8F0FF !important;
  opacity: 1 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
  font-family: "IBM Plex Sans", system-ui, sans-serif;
  color: #FFFFFF !important;
}
section[data-testid="stSidebar"] hr {
  border-color: rgba(255, 255, 255, 0.22) !important;
  margin: 0.65rem 0 !important;
}
.rc-sidebar-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #B8D0FF !important;
  margin: 0 0 0.35rem 0;
}
.rc-sidebar-mode {
  margin: 0 0 0.45rem 0 !important;
  font-size: 0.84rem !important;
  color: #E8F0FF !important;
  line-height: 1.35 !important;
}
.rc-sidebar-mode strong {
  color: #FFFFFF !important;
  font-weight: 650 !important;
}
/* Extra air under Demo scenarios before select */
.rc-demo-controls-label {
  margin: 0 0 0.7rem 0 !important;
}
section[data-testid="stSidebar"] .rc-scenario-preview {
  margin: 0.35rem 0 0.55rem 0;
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.28) !important;
  border-left-color: #B8D0FF !important;
}
section[data-testid="stSidebar"] .rc-scenario-preview-label {
  color: #B8D0FF !important;
}
section[data-testid="stSidebar"] .rc-scenario-preview-body {
  color: #F1F5F9 !important;
}

/* Sidebar selectbox: light fill on blue */
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  color: #0F172A !important;
  background-color: #EEF4FF !important;
  border-color: rgba(255, 255, 255, 0.55) !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div:hover,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
  background-color: #FFFFFF !important;
  border-color: #FFFFFF !important;
}
section[data-testid="stSidebar"] .stSelectbox svg,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg {
  fill: #0033A0 !important;
  color: #0033A0 !important;
}

/*
 * Keep sidebar collapse/expand always visible (Streamlit 1.6x).
 * Open: stSidebarCollapseButton lives in stSidebarHeader (scrolls with content
 * by default). Collapsed: stExpandSidebarButton sits in the app header
 * (legacy: stSidebarCollapsedControl). Pin both so they stay clickable.
 */
[data-testid="stSidebarHeader"] {
  position: sticky !important;
  top: 0 !important;
  z-index: 1000002 !important;
  /* Same solid as section[data-testid="stSidebar"] — opaque so scroll can't cover control */
  background: #0052FF !important;
  background-image: none !important;
  background-color: #0052FF !important;
  padding: 0.35rem 0.15rem 0.45rem 0 !important;
  margin-bottom: 0.35rem !important;
  pointer-events: auto !important;
}
/* Defensive: Streamlit sometimes paints nested header chrome separately */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] > div {
  background: #0052FF !important;
  background-image: none !important;
  background-color: #0052FF !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button {
  position: relative !important;
  z-index: 1000003 !important;
  visibility: visible !important;
  opacity: 1 !important;
  pointer-events: auto !important;
  color: #FFFFFF !important;
}
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
  color: #FFFFFF !important;
  fill: #FFFFFF !important;
  opacity: 1 !important;
}

/* Collapsed sidebar: pin expand control to the main canvas edge */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] {
  position: fixed !important;
  top: 0.55rem !important;
  left: 0.55rem !important;
  z-index: 1000005 !important;
  visibility: visible !important;
  opacity: 1 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  pointer-events: auto !important;
  color: #0F172A !important;
  background: rgba(255, 255, 255, 0.92) !important;
  border-radius: 6px !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.18) !important;
}
[data-testid="stSidebarCollapsedControl"] span,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stExpandSidebarButton"] span,
[data-testid="stExpandSidebarButton"] svg,
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
  color: #0F172A !important;
  fill: #0F172A !important;
  opacity: 1 !important;
}
/* Header must not steal clicks from the fixed expand control */
header[data-testid="stHeader"] {
  z-index: 999990 !important;
  background: transparent;
}
header[data-testid="stHeader"] [data-testid="stExpandSidebarButton"],
header[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"] {
  pointer-events: auto !important;
}

/* Minimize Streamlit chrome / hide Deploy (keep kind=header only — not headerNoPadding expand) */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton, [data-testid="stDeployButton"],
div[data-testid="stToolbar"] button[kind="header"],
div[data-testid="stToolbar"] a { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
</style>
"""
