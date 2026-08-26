"""Streamlit UI helpers — presentation only."""

from __future__ import annotations

import streamlit as st

from app.models.case import ReorgCase
from app.models.enums import ActionStatus, CaseStatus, IntegrationType, ReconciliationStatus


STATUS_COLORS = {
    CaseStatus.DRAFT: "gray",
    CaseStatus.INTERPRETED: "blue",
    CaseStatus.VALIDATED: "blue",
    CaseStatus.NEEDS_REVIEW: "orange",
    CaseStatus.PLANNED: "blue",
    CaseStatus.AWAITING_APPROVAL: "orange",
    CaseStatus.APPROVED: "green",
    CaseStatus.EXECUTING: "blue",
    CaseStatus.NEEDS_HUMAN_ACTION: "orange",
    CaseStatus.RECONCILING: "blue",
    CaseStatus.COMPLETED: "green",
    CaseStatus.FAILED: "red",
    CaseStatus.BLOCKED: "red",
}


def case_badge(case: ReorgCase) -> None:
    color = STATUS_COLORS.get(case.status, "gray")
    st.markdown(
        f"**Case** `{case.id}` &nbsp;|&nbsp; **Status:** "
        f":{color}[{case.status.value.replace('_', ' ').title()}]"
    )


def render_validation(case: ReorgCase) -> None:
    assert case.extracted_request is not None
    assert case.validation is not None
    req = case.extracted_request
    val = case.validation

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Effective date", req.effective_date or "—")
    c2.metric("People impacted", val.people_impacted_count)
    c3.metric("Confidence", f"{val.confidence:.0%}")
    c4.metric(
        "Safe to plan",
        "Yes" if val.is_safe_to_plan else "Needs review",
    )

    st.subheader("What the source claims")
    if req.summary:
        st.write(req.summary)
    if req.org_changes:
        for oc in req.org_changes:
            st.write(
                f"• **Org:** {oc.team_name}: "
                f"{oc.from_org_or_manager or '?'} → {oc.to_org_or_manager or '?'} "
                f"(claimed headcount: {oc.expected_headcount or '—'})"
            )
    if req.cost_center_changes:
        for cc in req.cost_center_changes:
            st.write(
                f"• **Cost center:** {cc.subject_name}: "
                f"{cc.from_cost_center or '?'} → {cc.to_cost_center or '?'}"
            )
    if req.exceptions:
        for ex in req.exceptions:
            st.write(
                f"• **Exception:** {ex.person_name} → "
                f"{ex.to_org_or_manager or ''} under {ex.to_manager or '—'}"
            )
    if req.assumptions:
        with st.expander("Extracted assumptions"):
            for a in req.assumptions:
                st.write(f"• {a}")

    st.subheader("Claimed vs verified approvals")
    for claim in val.claimed_vs_verified_approvals:
        if claim.independently_verified:
            st.success(
                f"**{claim.approver_role_or_name}** — verified. {claim.verification_note}"
            )
        else:
            st.warning(
                f"**{claim.approver_role_or_name}** — claimed in source, not verified.\n\n"
                f"> {claim.claim_text}\n\n"
                f"{claim.verification_note}"
            )
    if not val.claimed_vs_verified_approvals:
        st.info("No approval claims detected in source text.")

    st.subheader("Authoritative validation")
    if val.conflicts:
        st.error("Conflicts with systems of record")
        for c in val.conflicts:
            st.write(
                f"• **{c.code}**: {c.message} "
                f"(source: `{c.source_claim}` / authoritative: `{c.authoritative_finding}`)"
            )
    if val.issues:
        for issue in val.issues:
            if issue.code == "UNVERIFIED_APPROVAL_CLAIM":
                continue  # already shown above
            st.warning(f"**{issue.code}**: {issue.message}")
    if val.ambiguities:
        for amb in val.ambiguities:
            st.warning(f"**Ambiguity ({amb.field})**: {amb.description}")
    if not val.conflicts and not val.issues and not val.ambiguities:
        st.success("No conflicts or issues detected against fixture systems of record.")

    with st.expander("Verified entities"):
        for ent in val.verified_entities:
            mark = "✓" if ent.found else "✗"
            st.write(f"{mark} `{ent.entity_type}` **{ent.name}** ({ent.entity_id or '—'})")


def render_plan(case: ReorgCase) -> None:
    assert case.change_plan is not None
    plan = case.change_plan
    st.write(f"**Blast radius:** {plan.blast_radius_summary}")
    if plan.unresolved_risks:
        st.warning("Unresolved risks / open items")
        for r in plan.unresolved_risks:
            st.write(f"• {r}")

    st.markdown("#### Dependency-aware actions")
    for action in plan.ordered_actions:
        deps = ", ".join(action.depends_on) if action.depends_on else "—"
        itype = action.integration_type.value
        if action.integration_type == IntegrationType.MANUAL:
            badge = "🛠️ Manual"
        elif action.integration_type == IntegrationType.APPROVAL_GATE:
            badge = "🛂 Approval gate"
        else:
            badge = "⚙️ Automated"
        st.markdown(
            f"**`{action.id}`** {badge} — **{action.name}** ({action.system})  \n"
            f"Depends on: `{deps}`  \n"
            f"{action.description}"
        )


def render_approvals(case: ReorgCase) -> None:
    assert case.change_plan is not None
    for apr in case.change_plan.approval_requirements:
        if apr.granted:
            st.success(
                f"**{apr.role}** approved by {apr.granted_by} at {apr.granted_at}"
            )
        else:
            st.info(f"**{apr.role} required** — {apr.reason}")


def _action_status_label(status: ActionStatus) -> str:
    return status.value.replace("_", " ").title()


def render_execution(case: ReorgCase) -> None:
    assert case.change_plan is not None
    rows = []
    for a in case.change_plan.ordered_actions:
        rows.append(
            {
                "Action": a.id,
                "System": a.system,
                "Type": a.integration_type.value,
                "Status": _action_status_label(a.status),
                "Depends on": ", ".join(a.depends_on) or "—",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)

    for a in case.change_plan.ordered_actions:
        if a.error:
            st.error(f"`{a.id}`: {a.error}")


def render_human_tasks(case: ReorgCase) -> None:
    for task in case.human_tasks:
        st.markdown(f"### {task.title}")
        st.caption(f"Assigned to: **{task.assigned_role}** · Status: `{task.status.value}`")
        st.code(task.instructions)
        st.write("Required fields:")
        for k, v in task.required_fields.items():
            st.write(f"• **{k}**: `{v}`")


def render_reconciliation(case: ReorgCase) -> None:
    if not case.reconciliation:
        st.info("Reconciliation has not run yet.")
        return
    rec = case.reconciliation
    if rec.overall_status == ReconciliationStatus.PASSED:
        st.success(rec.summary)
    else:
        st.error(rec.summary)

    rows = [
        {
            "System": c.system,
            "Field": c.field,
            "Expected": c.expected,
            "Observed": c.observed,
            "Status": c.status.value.title(),
            "Notes": c.notes or "",
        }
        for c in rec.checks
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_audit(case: ReorgCase) -> None:
    for event in reversed(case.audit_log):
        st.write(
            f"`{event.timestamp}` · **{event.event_type.value}** · "
            f"{event.actor_type.value}:{event.actor_id} — {event.message}"
        )
