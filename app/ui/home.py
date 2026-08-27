"""Home screen: New Reorg Case + past cases list."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.data.scenarios import SCENARIOS
from app.workflow.engine import ReorgWorkflow


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


def render_home() -> None:
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
        st.write(
            "Paste an email, Slack message, or document. The workspace turns it into a "
            "governed case: interpret, validate, approve, execute, and reconcile."
        )
        if st.button("New Reorg Case", type="primary", use_container_width=True):
            st.session_state.view = "case"
            st.session_state.case = None
            st.session_state.raw_text = SCENARIOS["scenario_a_success"]["text"]
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
            st.session_state.raw_text = SCENARIOS[scenario_key]["text"]
            st.session_state.case = None
            st.session_state.workflow = ReorgWorkflow()
            st.session_state.view = "case"
            st.rerun()

    st.markdown("---")
    st.markdown("### Past cases")

    cases: list[dict[str, Any]] = st.session_state.get("case_index", [])
    if not cases:
        st.info("No cases yet. Create one with New Reorg Case.")
        return

    for row in cases:
        status = str(row.get("status", "unknown")).replace("_", " ").title()
        with st.container():
            c1, c2, c3 = st.columns([3, 1.2, 1])
            with c1:
                st.markdown(f"**{row.get('title') or row.get('id')}**")
                st.caption(
                    f"{row.get('id')} · Effective {row.get('effective_date') or '—'} · "
                    f"{row.get('updated') or ''}"
                )
                if row.get("note"):
                    st.caption(row["note"])
            with c2:
                st.write(status)
            with c3:
                if row.get("openable") and row.get("case_ref"):
                    if st.button("Open", key=f"open_{row['id']}", use_container_width=True):
                        st.session_state.case = row["case_ref"]
                        st.session_state.view = "case"
                        st.rerun()
                else:
                    st.caption("Sample")
            st.markdown("")


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
