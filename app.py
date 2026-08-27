"""
Reorg Workspace: portal for governed Reorg Cases.

Agents interpret and plan. Policies authorize. Tools execute.
Humans resolve ambiguity and high-impact decisions. The system verifies the result.
"""

from __future__ import annotations

import sys
from html import escape as html_escape
from pathlib import Path

# Ensure repo root on path when launched via `streamlit run app.py`
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.agents.llm import get_llm_provider, llm_mode_label
from app.data.scenarios import SCENARIOS, scenario_option_label
from app.models.enums import CaseStatus
from app.ui.auth import ensure_auth_cookie, is_authenticated, render_login, sign_out
from app.ui.components import (
    case_badge,
    render_approvals,
    render_audit,
    render_execution,
    render_human_tasks,
    render_plan,
    render_reconciliation,
    render_validation,
    stage_header,
)
from app.ui.home import render_home, seed_demo_cases, upsert_case_index
from app.ui.theme import THEME_CSS
from app.workflow.engine import ReorgWorkflow

st.set_page_config(
    page_title="Reorg Workspace",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _init_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "view" not in st.session_state:
        st.session_state.view = "home"
    if "workflow" not in st.session_state:
        st.session_state.workflow = ReorgWorkflow()
    if "case" not in st.session_state:
        st.session_state.case = None
    if "raw_text" not in st.session_state:
        st.session_state.raw_text = SCENARIOS["scenario_a_success"]["text"]
    # Keep widget key in sync: Streamlit text_area(key=) ignores value= after first mount.
    if "raw_input" not in st.session_state:
        st.session_state.raw_input = st.session_state.raw_text
    if "case_index" not in st.session_state:
        st.session_state.case_index = []


def _set_freeform_text(text: str) -> None:
    """Update freeform request text and the text_area widget key together."""
    st.session_state.raw_text = text
    st.session_state.raw_input = text


def _seed_case_index_if_empty() -> None:
    if not st.session_state.get("case_index"):
        st.session_state.case_index = seed_demo_cases()


def _render_sidebar(*, case_view: bool) -> None:
    auth_user = st.session_state.get("auth_user", "demo")

    st.markdown('<p class="rc-sidebar-label">Account</p>', unsafe_allow_html=True)
    st.caption(f"{auth_user} · demo session")
    if st.button("Sign out", use_container_width=True):
        sign_out()
        st.rerun()

    st.markdown("---")
    mode = llm_mode_label()
    st.markdown(
        f'<p class="rc-sidebar-mode">Interpretation: <strong>{html_escape(mode)}</strong></p>',
        unsafe_allow_html=True,
    )

    if not case_view:
        st.markdown("---")
        st.markdown('<p class="rc-sidebar-label">Workspace</p>', unsafe_allow_html=True)
        if st.button("Reset workspace", use_container_width=True):
            st.session_state.workflow = ReorgWorkflow()
            st.session_state.case = None
            _set_freeform_text(SCENARIOS["scenario_a_success"]["text"])
            st.session_state.case_index = seed_demo_cases()
            st.session_state.view = "home"
            st.rerun()
        return

    st.markdown("---")
    st.markdown(
        '<p class="rc-sidebar-label rc-demo-controls-label">Demo scenarios</p>',
        unsafe_allow_html=True,
    )
    scenario_key = st.selectbox(
        "Load a walkthrough scenario",
        options=list(SCENARIOS.keys()),
        format_func=scenario_option_label,
    )
    notes = SCENARIOS[scenario_key].get("notes") or ""
    if notes:
        st.markdown(
            f'<div class="rc-scenario-preview">'
            f'<p class="rc-scenario-preview-label">What to expect</p>'
            f'<p class="rc-scenario-preview-body">{html_escape(notes)}</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
    if st.button("Load scenario text", use_container_width=True):
        _set_freeform_text(SCENARIOS[scenario_key]["text"])
        st.session_state.case = None
        st.session_state.workflow = ReorgWorkflow()
        st.rerun()

    st.markdown("---")
    if st.button("Reset case", use_container_width=True):
        st.session_state.workflow = ReorgWorkflow()
        st.session_state.case = None
        _set_freeform_text(SCENARIOS["scenario_a_success"]["text"])
        st.session_state.view = "home"
        st.rerun()



def _render_case_view() -> None:
    wf: ReorgWorkflow = st.session_state.workflow

    st.markdown(
        """
        <div class="rc-brand">
          <div class="rc-brand-name">Reorg <span>Case</span></div>
          <p class="rc-brand-tagline">
            Turn freeform reorg requests into a governed case:
            interpret, validate, approve, execute, and reconcile across HR and Finance systems.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Back to workspace"):
        st.session_state.view = "home"
        st.rerun()

    case = st.session_state.case
    if case is not None:
        case_badge(case)

    tab_submit, tab_case, tab_plan, tab_exec, tab_recon, tab_audit = st.tabs(
        [
            "1. Submit",
            "2. Review case",
            "3. Plan & approve",
            "4. Execute",
            "5. Reconcile",
            "6. Audit",
        ]
    )

    with tab_submit:
        stage_header(
            "Stage 1 · Intake",
            "Submit reorg request",
            "Paste the freeform request (email, Slack, or document). "
            "There is no structured event to subscribe to; analysis starts here.",
        )
        raw = st.text_area(
            "Freeform reorg request",
            value=st.session_state.raw_text,
            height=220,
            key="raw_input",
        )
        # Widget key is canonical while the area is mounted; keep raw_text aligned.
        st.session_state.raw_text = raw

        if st.button("Analyze reorg", type="primary"):
            if not raw.strip():
                st.error("Paste a reorg request first.")
            else:
                with st.spinner("Interpreting → validating → planning…"):
                    # Fresh store per analysis so demos are repeatable
                    st.session_state.workflow = ReorgWorkflow()
                    wf = st.session_state.workflow
                    new_case = wf.create_case(raw)
                    st.session_state.case = wf.analyze(new_case)
                    upsert_case_index(st.session_state.case)
                st.success(
                    f"Created case {st.session_state.case.id}. "
                    "Open Review case to check validation, then Plan & approve."
                )
                st.rerun()

    if case is None:
        for tab in (tab_case, tab_plan, tab_exec, tab_recon, tab_audit):
            with tab:
                st.info("Submit and analyze a reorg request to populate this view.")
        return

    with tab_case:
        stage_header(
            "Stage 2 · Interpret & validate",
            "Review the Reorg Case",
            "The model proposes structure. Authoritative systems verify. "
            "Natural-language approval claims are not execution permission.",
        )
        if case.extracted_request and case.validation:
            render_validation(case)
        with st.expander("Original source material", expanded=False):
            st.code(case.source.raw_text)

    with tab_plan:
        stage_header(
            "Stage 3 · Plan & approve",
            "Proposed execution plan",
            "Review the dependency-aware plan, unresolved risks, and required approvals "
            "before any system is updated.",
        )
        if not case.change_plan:
            st.warning("No plan generated.")
        else:
            render_plan(case)
            st.markdown("---")
            st.markdown("#### Approval gate")
            st.write(
                "Policy determines why approval is required, what runs after approval, "
                "and what remains unresolved."
            )
            render_approvals(case)

            can_approve = case.status in (
                CaseStatus.AWAITING_APPROVAL,
                CaseStatus.NEEDS_REVIEW,
                CaseStatus.PLANNED,
            ) or (
                case.change_plan
                and not all(a.granted for a in case.change_plan.approval_requirements)
            )

            if can_approve and case.change_plan:
                st.markdown("#### Grant approvals")
                st.write(
                    "After approval the system will: update HRIS → headcount & cost "
                    "allocation → create a **manual GL mapping task** → reporting → reconcile."
                )
                if case.validation and not case.validation.is_safe_to_plan:
                    st.error(
                        "Validation found blocking conflicts. You may still approve for "
                        "demo purposes, but production policy would likely refuse execution."
                    )
                granted_by = st.text_input(
                    "Approver identity (demo)",
                    value="hr.ops.lead@example.com",
                )
                if st.button("Approve plan", type="primary"):
                    st.session_state.case = wf.approve(case, granted_by=granted_by)
                    upsert_case_index(st.session_state.case)
                    st.success("Approvals granted. Continue to Execute.")
                    st.rerun()

    with tab_exec:
        stage_header(
            "Stage 4 · Execute",
            "Run the approved plan",
            "Automated adapters update connected systems. Steps without an API pause "
            "for a named human owner; the workflow stays owned by the case.",
        )
        if not case.change_plan:
            st.info("No plan yet.")
        else:
            all_granted = all(
                a.granted for a in case.change_plan.approval_requirements if a.required
            )
            if not all_granted:
                st.warning("Approvals not granted yet; execution is blocked by policy.")
            else:
                if case.status in (
                    CaseStatus.APPROVED,
                    CaseStatus.AWAITING_APPROVAL,
                ):
                    if st.button("Run execution", type="primary"):
                        st.session_state.case = wf.execute(case)
                        upsert_case_index(st.session_state.case)
                        st.rerun()

            render_execution(case)

            pending_manual = [
                t
                for t in case.human_tasks
                if t.status.value == "needs_human_action"
            ]
            if pending_manual or case.status == CaseStatus.NEEDS_HUMAN_ACTION:
                st.markdown("---")
                st.markdown("#### Manual GL mapping")
                st.write(
                    "GL mapping has no API in this prototype. Finance Operations completes "
                    "the entry; the case tracks the task and continues when marked done."
                )
                render_human_tasks(case)

                expected_cc = ""
                if case.change_plan:
                    gl_action = next(
                        (
                            a
                            for a in case.change_plan.ordered_actions
                            if a.id == "update_gl_mapping"
                        ),
                        None,
                    )
                    if gl_action:
                        expected_cc = str(gl_action.payload.get("new_cost_center") or "")

                entered = st.text_input(
                    "Cost center entered in GL system",
                    value=expected_cc,
                    key="gl_entered",
                )
                simulate_bad = st.checkbox(
                    "Simulate incorrect GL entry (demo failure path)",
                    value=False,
                    help="Writes the old cost center into GL to show reconciliation failure.",
                )
                if st.button("Mark complete", type="primary"):
                    st.session_state.case = wf.complete_manual_gl(
                        case,
                        entered_cost_center=entered or expected_cc,
                        simulate_incorrect_entry=simulate_bad,
                    )
                    upsert_case_index(st.session_state.case)
                    st.rerun()

    with tab_recon:
        stage_header(
            "Stage 5 · Reconcile",
            "Expected vs observed",
            "Completion means expected state matches observed state, "
            "not merely that every task reported success.",
        )
        render_reconciliation(case)

    with tab_audit:
        stage_header(
            "Stage 6 · Audit",
            "Decision and mutation trail",
            "Sensitive raw values are minimized. Events record interpretation, "
            "approvals, writes, and reconciliation outcomes.",
        )
        render_audit(case)


def main() -> None:
    _init_state()

    if not is_authenticated():
        render_login()
        return

    ensure_auth_cookie()
    _seed_case_index_if_empty()
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    view = st.session_state.get("view", "home")
    case_view = view == "case"

    with st.sidebar:
        _render_sidebar(case_view=case_view)

    if case_view:
        _render_case_view()
    else:
        render_home()


if __name__ == "__main__":
    main()
