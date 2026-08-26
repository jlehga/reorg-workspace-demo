"""
Reorg Case — Agentic-Driven Reorganization Prototype

Agents interpret and plan. Policies authorize. Tools execute.
Humans resolve ambiguity and high-impact decisions. The system verifies the result.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root on path when launched via `streamlit run app.py`
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.data.scenarios import SCENARIOS
from app.models.enums import CaseStatus
from app.ui.components import (
    case_badge,
    render_approvals,
    render_audit,
    render_execution,
    render_human_tasks,
    render_plan,
    render_reconciliation,
    render_validation,
)
from app.workflow.engine import ReorgWorkflow

st.set_page_config(
    page_title="Reorg Case",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Avoid broken emoji — use text
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _init_state() -> None:
    if "workflow" not in st.session_state:
        st.session_state.workflow = ReorgWorkflow()
    if "case" not in st.session_state:
        st.session_state.case = None
    if "raw_text" not in st.session_state:
        st.session_state.raw_text = SCENARIOS["scenario_a_success"]["text"]


def main() -> None:
    _init_state()
    wf: ReorgWorkflow = st.session_state.workflow

    st.title("Reorg Case")
    st.caption(
        "Agents interpret and plan · Policies authorize · Tools execute · "
        "Humans resolve ambiguity · The system verifies the result"
    )

    with st.sidebar:
        st.header("Demo controls")
        scenario_key = st.selectbox(
            "Load scenario",
            options=list(SCENARIOS.keys()),
            format_func=lambda k: SCENARIOS[k]["label"],
        )
        if st.button("Load scenario text", use_container_width=True):
            st.session_state.raw_text = SCENARIOS[scenario_key]["text"]
            st.session_state.case = None
            st.session_state.workflow = ReorgWorkflow()
            st.rerun()

        st.markdown("---")
        st.markdown(f"**Scenario notes**\n\n{SCENARIOS[scenario_key]['notes']}")
        st.markdown("---")
        st.caption(
            f"Extractor: `{wf.interpreter.provider.name}` · "
            "Set `OPENAI_API_KEY` to use live LLM extraction."
        )
        if st.button("Reset workspace", use_container_width=True):
            st.session_state.workflow = ReorgWorkflow()
            st.session_state.case = None
            st.session_state.raw_text = SCENARIOS["scenario_a_success"]["text"]
            st.rerun()

    case = st.session_state.case

    tab_submit, tab_case, tab_plan, tab_exec, tab_recon, tab_audit = st.tabs(
        [
            "1. Submit",
            "2. Reorg Case",
            "3. Plan & Approve",
            "4. Execution",
            "5. Reconciliation",
            "6. Audit",
        ]
    )

    with tab_submit:
        st.subheader("Submit reorg request")
        st.write(
            "Reorg changes arrive as freeform text — email, Slack, or a document. "
            "There is no structured event to subscribe to."
        )
        raw = st.text_area(
            "Freeform reorg request",
            value=st.session_state.raw_text,
            height=220,
            key="raw_input",
        )
        st.session_state.raw_text = raw

        if st.button("Analyze Reorg", type="primary"):
            if not raw.strip():
                st.error("Paste a reorg request first.")
            else:
                with st.spinner("Interpreting → validating → planning…"):
                    # Fresh store per analysis so demos are repeatable
                    st.session_state.workflow = ReorgWorkflow()
                    wf = st.session_state.workflow
                    new_case = wf.create_case(raw)
                    st.session_state.case = wf.analyze(new_case)
                st.success(
                    f"Created case {st.session_state.case.id}. "
                    "Review validation and the proposed plan."
                )
                st.rerun()

    if case is None:
        for tab in (tab_case, tab_plan, tab_exec, tab_recon, tab_audit):
            with tab:
                st.info("Submit and analyze a reorg request to populate this view.")
        return

    case_badge(case)

    with tab_case:
        st.subheader("Interpreted Reorg Case")
        st.write(
            "The model proposes structure. Authoritative systems verify. "
            "Natural-language approval claims are **not** execution permission."
        )
        if case.extracted_request and case.validation:
            render_validation(case)
        with st.expander("Original source material", expanded=False):
            st.code(case.source.raw_text)

    with tab_plan:
        st.subheader("Proposed execution plan")
        if not case.change_plan:
            st.warning("No plan generated.")
        else:
            render_plan(case)
            st.markdown("---")
            st.subheader("Approval gate")
            st.write(
                "Why approval is required, what will happen after approval, "
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
                st.markdown("#### Approve plan")
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
                if st.button("Approve Plan", type="primary"):
                    st.session_state.case = wf.approve(case, granted_by=granted_by)
                    st.success("Approvals granted. Proceed to Execution.")
                    st.rerun()

    with tab_exec:
        st.subheader("Execution status")
        if not case.change_plan:
            st.info("No plan yet.")
        else:
            all_granted = all(
                a.granted for a in case.change_plan.approval_requirements if a.required
            )
            if not all_granted:
                st.warning("Approvals not granted yet — execution is blocked by policy.")
            else:
                if case.status in (
                    CaseStatus.APPROVED,
                    CaseStatus.AWAITING_APPROVAL,
                ):
                    if st.button("Run execution", type="primary"):
                        st.session_state.case = wf.execute(case)
                        st.rerun()

            render_execution(case)

            pending_manual = [
                t
                for t in case.human_tasks
                if t.status.value == "needs_human_action"
            ]
            if pending_manual or case.status == CaseStatus.NEEDS_HUMAN_ACTION:
                st.markdown("---")
                st.subheader("Human-mediated step (no API)")
                st.write(
                    "Automation does not mean removing humans — it means removing "
                    "humans as the orchestration layer. The system owns the workflow; "
                    "Finance Operations is the actuator for GL mapping."
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
                if st.button("Mark Complete", type="primary"):
                    st.session_state.case = wf.complete_manual_gl(
                        case,
                        entered_cost_center=entered or expected_cc,
                        simulate_incorrect_entry=simulate_bad,
                    )
                    st.rerun()

    with tab_recon:
        st.subheader("Reconciliation")
        st.write(
            "Completion means expected state matches observed state — "
            "not merely that every task reported success."
        )
        render_reconciliation(case)

    with tab_audit:
        st.subheader("Audit trail")
        st.caption("Sensitive raw values are minimized; events record decisions and mutations.")
        render_audit(case)


if __name__ == "__main__":
    main()
