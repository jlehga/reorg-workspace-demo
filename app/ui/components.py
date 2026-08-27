"""Streamlit UI helpers — presentation only."""

from __future__ import annotations

import html

import streamlit as st

from app.models.case import ReorgCase
from app.models.enums import ActionStatus, CaseStatus, IntegrationType, ReconciliationStatus


STATUS_BADGE_CLASS = {
    CaseStatus.DRAFT: "rc-badge-gray",
    CaseStatus.INTERPRETED: "rc-badge-blue",
    CaseStatus.VALIDATED: "rc-badge-blue",
    CaseStatus.NEEDS_REVIEW: "rc-badge-orange",
    CaseStatus.PLANNED: "rc-badge-blue",
    CaseStatus.AWAITING_APPROVAL: "rc-badge-orange",
    CaseStatus.APPROVED: "rc-badge-green",
    CaseStatus.EXECUTING: "rc-badge-blue",
    CaseStatus.NEEDS_HUMAN_ACTION: "rc-badge-orange",
    CaseStatus.RECONCILING: "rc-badge-blue",
    CaseStatus.COMPLETED: "rc-badge-green",
    CaseStatus.FAILED: "rc-badge-red",
    CaseStatus.BLOCKED: "rc-badge-red",
}


def stage_header(step: str, title: str, help_text: str) -> None:
    """Framing block so nontechnical users know what this stage is for."""
    st.markdown(
        f"""
        <div class="rc-stage">
          <p class="rc-stage-label">{step}</p>
          <p class="rc-stage-title">{title}</p>
          <p class="rc-stage-help">{help_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def case_badge(case: ReorgCase) -> None:
    badge_cls = STATUS_BADGE_CLASS.get(case.status, "rc-badge-gray")
    label = case.status.value.replace("_", " ").title()
    case_id = html.escape(case.id)
    st.markdown(
        f"""
        <div class="rc-status-strip">
          <span class="rc-status-id">Case <code>{case_id}</code></span>
          <span class="rc-badge {badge_cls}">{html.escape(label)}</span>
        </div>
        """,
        unsafe_allow_html=True,
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

    st.markdown("#### What the source claims")
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

    st.markdown("#### Claimed vs verified approvals")
    st.caption(
        "Approvals mentioned in email or Slack are treated as claims until "
        "confirmed in an authoritative approvals ledger."
    )
    for claim in val.claimed_vs_verified_approvals:
        role = html.escape(claim.approver_role_or_name)
        if claim.independently_verified:
            note = html.escape(claim.verification_note or "")
            st.markdown(
                f"""
                <div class="rc-callout rc-callout-verified">
                  <span class="rc-pill rc-pill-ok">Verified</span>
                  <p class="rc-callout-title">{role}</p>
                  <p class="rc-callout-body">{note}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            note = html.escape(claim.verification_note or "")
            quote = html.escape(claim.claim_text or "")
            st.markdown(
                f"""
                <div class="rc-callout rc-callout-unverified">
                  <span class="rc-pill rc-pill-warn">Unverified claim</span>
                  <p class="rc-callout-title">{role}</p>
                  <div class="rc-callout-quote">{quote}</div>
                  <p class="rc-callout-body">{note}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    if not val.claimed_vs_verified_approvals:
        st.info("No approval claims detected in source text.")

    st.markdown("#### Authoritative validation")
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

    st.markdown("#### Ordered actions")
    st.caption("Actions run in dependency order. Manual steps pause the workflow until completed.")
    for action in plan.ordered_actions:
        deps = html.escape(", ".join(action.depends_on) if action.depends_on else "—")
        if action.integration_type == IntegrationType.MANUAL:
            type_cls = "rc-type-manual"
            type_label = "Manual"
        elif action.integration_type == IntegrationType.APPROVAL_GATE:
            type_cls = "rc-type-gate"
            type_label = "Approval gate"
        else:
            type_cls = "rc-type-auto"
            type_label = "Automated"
        st.markdown(
            f"""
            <div class="rc-action">
              <div class="rc-action-top">
                <span class="rc-action-id">{html.escape(action.id)}</span>
                <span class="rc-type {type_cls}">{type_label}</span>
                <span class="rc-action-name">{html.escape(action.name)}</span>
              </div>
              <p class="rc-action-meta">System: {html.escape(action.system)} · Depends on: {deps}</p>
              <p class="rc-action-desc">{html.escape(action.description)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_approvals(case: ReorgCase) -> None:
    assert case.change_plan is not None
    for apr in case.change_plan.approval_requirements:
        role = html.escape(apr.role)
        if apr.granted:
            granted_at = html.escape(str(apr.granted_at or "—"))
            granted_by = html.escape(apr.granted_by or "—")
            st.markdown(
                f"""
                <div class="rc-callout rc-callout-granted">
                  <span class="rc-pill rc-pill-ok">Granted</span>
                  <p class="rc-callout-title">{role}</p>
                  <p class="rc-callout-body">Approved by {granted_by} at {granted_at}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            reason = html.escape(apr.reason)
            st.markdown(
                f"""
                <div class="rc-callout rc-callout-required">
                  <span class="rc-pill rc-pill-req">Required</span>
                  <p class="rc-callout-title">{role} approval</p>
                  <p class="rc-callout-body">{reason}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


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
        status_label = task.status.value.replace("_", " ").title()
        st.markdown(f"### {task.title}")
        st.caption(f"Assigned to: **{task.assigned_role}** · Status: {status_label}")
        st.code(task.instructions)
        st.write("Required fields:")
        for k, v in task.required_fields.items():
            st.write(f"• **{k}**: `{v}`")


def render_reconciliation(case: ReorgCase) -> None:
    if not case.reconciliation:
        st.info("Reconciliation has not run yet. Complete execution (including any manual GL step) first.")
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
