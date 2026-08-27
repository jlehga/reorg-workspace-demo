"""Home screen: New Reorg Case + past cases list."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from app.data.scenarios import SCENARIOS
from app.workflow.engine import ReorgWorkflow

_STATUS_BADGE = {
    "completed": "rc-badge-green",
    "failed": "rc-badge-red",
    "blocked": "rc-badge-red",
    "executing": "rc-badge-blue",
    "reconciling": "rc-badge-blue",
    "interpreted": "rc-badge-blue",
    "validated": "rc-badge-blue",
    "planned": "rc-badge-blue",
    "approved": "rc-badge-blue",
    "awaiting_approval": "rc-badge-orange",
    "needs_review": "rc-badge-orange",
    "needs_human_action": "rc-badge-orange",
    "draft": "rc-badge-gray",
}


def seed_demo_cases() -> list[dict[str, Any]]:
    """Lightweight past-case rows for an empty workspace (not full workflow objects)."""
    return [
        {
            "id": "RC-DEMO001",
            "title": "Payments Engineering → Jane Smith",
            "status": "completed",
            "effective_date": "2026-09-01",
            "updated": "Demo sample",
            "openable": False,
            "note": "Sample completed case for the home list. Start a new case to run the live workflow.",
        },
        {
            "id": "RC-DEMO002",
            "title": "Ledger move (blocked on GL)",
            "status": "failed",
            "effective_date": "2026-08-12",
            "updated": "Demo sample",
            "openable": False,
            "note": "Sample failed reconciliation. Use Simulate incorrect GL entry on a live case to reproduce.",
        },
    ]


def _status_badge(status_raw: str) -> str:
    key = str(status_raw or "unknown").strip().lower().replace(" ", "_")
    label = html.escape(key.replace("_", " ").title())
    klass = _STATUS_BADGE.get(key, "rc-badge-gray")
    return f'<span class="rc-badge {klass}">{label}</span>'


def _case_row_html(
    row: dict[str, Any],
    *,
    action_html: str | None = "Sample",
) -> str:
    title = html.escape(str(row.get("title") or row.get("id") or "Reorg Case"))
    case_id = html.escape(str(row.get("id") or "—"))
    effective = html.escape(str(row.get("effective_date") or "—"))
    updated = html.escape(str(row.get("updated") or ""))
    note = row.get("note")
    note_html = (
        f'<p class="rc-case-note">{html.escape(str(note))}</p>' if note else ""
    )
    meta = f"{case_id} · Effective {effective}"
    if updated:
        meta += f" · {updated}"
    openable = action_html is None
    row_klass = "rc-case-row rc-case-row-openable" if openable else "rc-case-row"
    action_block = (
        ""
        if openable
        else f'<div class="rc-case-action">{action_html}</div>'
    )
    # Single-line HTML: Streamlit markdown breaks multi-block HTML on blank lines.
    return (
        f'<div class="{row_klass}">'
        f'<div class="rc-case-main">'
        f'<p class="rc-case-title">{title}</p>'
        f'<p class="rc-case-meta">{meta}</p>'
        f"{note_html}"
        f"</div>"
        f'<div class="rc-case-status">{_status_badge(str(row.get("status", "unknown")))}</div>'
        f"{action_block}"
        f"</div>"
    )


def render_home() -> None:
    st.markdown('<div class="rc-home-root" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="rc-brand">
          <div class="rc-brand-name">Reorg <span>Workspace</span></div>
          <p class="rc-brand-tagline">
            Open a past case or start a new Reorg Case from a freeform request.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### New Reorg Case")
        # Use a div (not <p>): Streamlit strips class attributes from bare paragraphs.
        st.markdown(
            '<div class="rc-home-lead">'
            "Paste an email, Slack message, or document. The workspace turns it into a "
            "governed case: interpret, validate, approve, execute, and reconcile."
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("New Reorg Case", type="primary", use_container_width=True):
            st.session_state.view = "case"
            st.session_state.case = None
            text = SCENARIOS["scenario_a_success"]["text"]
            st.session_state.raw_text = text
            st.session_state.raw_input = text
            st.session_state.workflow = ReorgWorkflow()
            st.rerun()

    with right:
        st.markdown("### Quick load")
        st.caption("Optional demo scenarios for the interview walkthrough.")
        scenario_key = st.selectbox(
            "Scenario",
            options=list(SCENARIOS.keys()),
            format_func=lambda k: SCENARIOS[k]["label"],
        )
        if st.button("Start from scenario", use_container_width=True):
            text = SCENARIOS[scenario_key]["text"]
            st.session_state.raw_text = text
            st.session_state.raw_input = text
            st.session_state.case = None
            st.session_state.workflow = ReorgWorkflow()
            st.session_state.view = "case"
            st.rerun()

    st.markdown(
        '<div class="rc-home-section-label">Past cases</div>',
        unsafe_allow_html=True,
    )

    cases: list[dict[str, Any]] = st.session_state.get("case_index", [])
    if not cases:
        st.info("No cases yet. Create one with New Reorg Case.")
        return

    # One HTML list (no blank lines) so Streamlit keeps markup as HTML.
    sample_rows: list[str] = []
    openable_rows: list[dict[str, Any]] = []
    for row in cases:
        if row.get("openable") and row.get("case_ref"):
            if sample_rows:
                st.markdown(
                    f'<div class="rc-case-list">{"".join(sample_rows)}</div>',
                    unsafe_allow_html=True,
                )
                sample_rows = []
            openable_rows.append(row)
            main = st.columns([6.2, 1])
            with main[0]:
                st.markdown(
                    f'<div class="rc-case-list">{_case_row_html(row, action_html=None)}</div>',
                    unsafe_allow_html=True,
                )
            with main[1]:
                st.markdown('<div class="rc-case-open-slot"></div>', unsafe_allow_html=True)
                if st.button("Open", key=f"open_{row['id']}", use_container_width=True):
                    st.session_state.case = row["case_ref"]
                    st.session_state.view = "case"
                    st.rerun()
        else:
            sample_rows.append(_case_row_html(row, action_html="Sample"))

    if sample_rows:
        st.markdown(
            f'<div class="rc-case-list">{"".join(sample_rows)}</div>',
            unsafe_allow_html=True,
        )


def upsert_case_index(case) -> None:
    """Keep a home-list entry for a live case object."""
    from app.models.audit import utc_now_iso

    title = "Reorg Case"
    if case.extracted_request and case.extracted_request.summary:
        title = case.extracted_request.summary
    elif case.extracted_request and case.extracted_request.org_changes:
        title = case.extracted_request.org_changes[0].team_name

    effective = None
    if case.extracted_request:
        effective = case.extracted_request.effective_date

    entry = {
        "id": case.id,
        "title": title,
        "status": case.status.value,
        "effective_date": effective,
        "updated": utc_now_iso()[:19].replace("T", " ") + " UTC",
        "openable": True,
        "case_ref": case,
        "note": None,
    }

    index: list = st.session_state.setdefault("case_index", [])
    # Replace existing id
    index = [e for e in index if e.get("id") != case.id]
    index.insert(0, entry)
    st.session_state.case_index = index
