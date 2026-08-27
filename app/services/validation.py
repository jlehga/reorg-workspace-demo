"""Authoritative-system validation — deterministic, not LLM."""

from __future__ import annotations

from app.data.store import EnterpriseStore
from app.models.case import ReorgCase
from app.models.enums import (
    ActorType,
    AuditEventType,
    CaseStatus,
    ValidationSeverity,
)
from app.models.extraction import (
    Ambiguity,
    ClaimedApproval,
    ValidationIssue,
    ValidationResult,
    VerifiedEntity,
)
from app.utils.audit import append_audit


class ValidationService:
    def __init__(self, store: EnterpriseStore) -> None:
        self.store = store

    def validate(self, case: ReorgCase) -> ValidationResult:
        assert case.extracted_request is not None
        req = case.extracted_request

        verified: list[VerifiedEntity] = []
        issues: list[ValidationIssue] = []
        conflicts: list[ValidationIssue] = []
        ambiguities: list[Ambiguity] = list(req.ambiguities)

        primary_team = None
        for org_change in req.org_changes:
            team = self.store.find_team_by_name(org_change.team_name)
            if not team:
                conflicts.append(
                    ValidationIssue(
                        code="TEAM_NOT_FOUND",
                        message=f"Team '{org_change.team_name}' was not found in the org directory.",
                        severity=ValidationSeverity.CONFLICT,
                        related_entity=org_change.team_name,
                        source_claim=org_change.team_name,
                        authoritative_finding="No matching team record",
                    )
                )
                verified.append(
                    VerifiedEntity(
                        entity_type="team",
                        name=org_change.team_name,
                        found=False,
                    )
                )
                continue

            primary_team = team
            members = self.store.team_members(team["id"])
            verified.append(
                VerifiedEntity(
                    entity_type="team",
                    name=team["name"],
                    entity_id=team["id"],
                    found=True,
                    details={
                        "member_count": len(members),
                        "org_id": team["org_id"],
                        "cost_center": team["cost_center"],
                        "manager_id": team["manager_id"],
                    },
                )
            )
            append_audit(
                case,
                AuditEventType.ENTITY_VALIDATED,
                f"Verified team '{team['name']}' ({team['id']}) with {len(members)} members.",
                metadata={"team_id": team["id"], "member_count": len(members)},
            )

            if org_change.expected_headcount is not None:
                actual = len(members)
                if org_change.expected_headcount != actual:
                    conflicts.append(
                        ValidationIssue(
                            code="HEADCOUNT_MISMATCH",
                            message=(
                                f"Source claims {org_change.expected_headcount} people on "
                                f"{team['name']}; HRIS shows {actual}."
                            ),
                            severity=ValidationSeverity.CONFLICT,
                            related_entity=team["name"],
                            source_claim=str(org_change.expected_headcount),
                            authoritative_finding=str(actual),
                        )
                    )

            # Validate from/to managers
            for label, name in (
                ("from_manager", org_change.from_org_or_manager),
                ("to_manager", org_change.to_org_or_manager),
            ):
                if not name:
                    continue
                emp = self.store.find_employee_by_name(name)
                if not emp:
                    # also try org name
                    org_hit = next(
                        (
                            o
                            for o in self.store.orgs.values()
                            if name.lower() in o["name"].lower()
                        ),
                        None,
                    )
                    if org_hit:
                        verified.append(
                            VerifiedEntity(
                                entity_type="org",
                                name=org_hit["name"],
                                entity_id=org_hit["id"],
                                found=True,
                            )
                        )
                        continue
                    conflicts.append(
                        ValidationIssue(
                            code="PERSON_NOT_FOUND",
                            message=f"'{name}' referenced as {label} was not found.",
                            severity=ValidationSeverity.CONFLICT,
                            related_entity=name,
                            source_claim=name,
                            authoritative_finding="Not in employee directory",
                        )
                    )
                    verified.append(
                        VerifiedEntity(entity_type="person", name=name, found=False)
                    )
                    continue

                verified.append(
                    VerifiedEntity(
                        entity_type="person",
                        name=emp["name"],
                        entity_id=emp["id"],
                        found=True,
                        details={
                            "is_manager": emp["is_manager"],
                            "eligible_org_receiver": emp.get("eligible_org_receiver", False),
                            "title": emp["title"],
                        },
                    )
                )

                if label == "to_manager" and not emp.get("eligible_org_receiver", False):
                    issues.append(
                        ValidationIssue(
                            code="INELIGIBLE_RECEIVER",
                            message=(
                                f"{emp['name']} is not marked eligible to receive an organization."
                            ),
                            severity=ValidationSeverity.ERROR,
                            related_entity=emp["name"],
                        )
                    )

                if label == "from_manager" and primary_team:
                    # Mike Chen should be leader of Consumer / current org
                    current_org = self.store.orgs.get(primary_team["org_id"])
                    if current_org and current_org["leader_id"] != emp["id"]:
                        # Soft check: also allow if manager chain includes them
                        team_mgr = self.store.employees.get(primary_team["manager_id"])
                        chain_ok = False
                        if team_mgr and team_mgr.get("manager_id") == emp["id"]:
                            chain_ok = True
                        if not chain_ok and current_org["leader_id"] != emp["id"]:
                            issues.append(
                                ValidationIssue(
                                    code="FROM_MANAGER_MISMATCH",
                                    message=(
                                        f"Source says team is under {emp['name']}; "
                                        f"org leader is "
                                        f"{self.store.employees[current_org['leader_id']]['name']}."
                                    ),
                                    severity=ValidationSeverity.WARNING,
                                    related_entity=emp["name"],
                                    source_claim=emp["name"],
                                    authoritative_finding=self.store.employees[
                                        current_org["leader_id"]
                                    ]["name"],
                                )
                            )

        # Cost centers
        for cc_change in req.cost_center_changes:
            for label, cc_id in (
                ("from", cc_change.from_cost_center),
                ("to", cc_change.to_cost_center),
            ):
                if not cc_id:
                    continue
                cc = self.store.cost_centers.get(cc_id.upper())
                if not cc:
                    conflicts.append(
                        ValidationIssue(
                            code="COST_CENTER_NOT_FOUND",
                            message=f"Cost center {cc_id} does not exist.",
                            severity=ValidationSeverity.CONFLICT,
                            related_entity=cc_id,
                            source_claim=cc_id,
                            authoritative_finding="Not found",
                        )
                    )
                    verified.append(
                        VerifiedEntity(
                            entity_type="cost_center", name=cc_id, found=False
                        )
                    )
                else:
                    verified.append(
                        VerifiedEntity(
                            entity_type="cost_center",
                            name=cc["id"],
                            entity_id=cc["id"],
                            found=True,
                            details={"active": cc["active"], "name": cc["name"]},
                        )
                    )
                    if not cc["active"]:
                        conflicts.append(
                            ValidationIssue(
                                code="COST_CENTER_INACTIVE",
                                message=f"Cost center {cc_id} exists but is inactive.",
                                severity=ValidationSeverity.CONFLICT,
                                related_entity=cc_id,
                                source_claim=cc_id,
                                authoritative_finding="inactive",
                            )
                        )
                    if (
                        label == "from"
                        and primary_team
                        and primary_team["cost_center"] != cc["id"]
                    ):
                        conflicts.append(
                            ValidationIssue(
                                code="COST_CENTER_MISMATCH",
                                message=(
                                    f"Source says current CC is {cc_id}; team is on "
                                    f"{primary_team['cost_center']}."
                                ),
                                severity=ValidationSeverity.CONFLICT,
                                related_entity=cc_id,
                                source_claim=cc_id,
                                authoritative_finding=primary_team["cost_center"],
                            )
                        )

        # Exceptions
        for exc in req.exceptions:
            emp = self.store.find_employee_by_name(exc.person_name)
            if not emp:
                conflicts.append(
                    ValidationIssue(
                        code="EXCEPTION_PERSON_NOT_FOUND",
                        message=f"Exception person '{exc.person_name}' not found.",
                        severity=ValidationSeverity.CONFLICT,
                        related_entity=exc.person_name,
                    )
                )
            else:
                on_team = (
                    primary_team is not None and emp.get("team_id") == primary_team["id"]
                )
                verified.append(
                    VerifiedEntity(
                        entity_type="person",
                        name=emp["name"],
                        entity_id=emp["id"],
                        found=True,
                        details={"on_primary_team": on_team, "team_id": emp.get("team_id")},
                    )
                )
                if primary_team and not on_team:
                    issues.append(
                        ValidationIssue(
                            code="EXCEPTION_NOT_ON_TEAM",
                            message=(
                                f"{emp['name']} is listed as an exception but is not a "
                                f"member of {primary_team['name']}."
                            ),
                            severity=ValidationSeverity.WARNING,
                            related_entity=emp["name"],
                        )
                    )
                if exc.to_manager:
                    mgr = self.store.find_employee_by_name(exc.to_manager)
                    if not mgr:
                        conflicts.append(
                            ValidationIssue(
                                code="EXCEPTION_MANAGER_NOT_FOUND",
                                message=f"Exception target manager '{exc.to_manager}' not found.",
                                severity=ValidationSeverity.CONFLICT,
                                related_entity=exc.to_manager,
                            )
                        )
                    else:
                        verified.append(
                            VerifiedEntity(
                                entity_type="person",
                                name=mgr["name"],
                                entity_id=mgr["id"],
                                found=True,
                            )
                        )

        # Claimed approvals vs authoritative approval store
        verified_claims: list[ClaimedApproval] = []
        target_ccs = [
            c.to_cost_center
            for c in req.cost_center_changes
            if c.to_cost_center
        ] + [
            c.from_cost_center
            for c in req.cost_center_changes
            if c.from_cost_center
        ]
        keywords = [o.team_name for o in req.org_changes] or ["Payments"]

        for claim in req.claimed_approvals:
            updated = claim.model_copy(deep=True)
            if "finance" in claim.approver_role_or_name.lower():
                recorded = self.store.find_finance_approval(
                    [c for c in target_ccs if c], keywords
                )
                if recorded:
                    updated.independently_verified = True
                    updated.verification_note = (
                        f"Verified against approval record {recorded['id']}."
                    )
                else:
                    updated.independently_verified = False
                    updated.verification_note = (
                        "Finance approval is referenced in the source material but "
                        "could not be independently verified."
                    )
                    issues.append(
                        ValidationIssue(
                            code="UNVERIFIED_APPROVAL_CLAIM",
                            message=updated.verification_note,
                            severity=ValidationSeverity.WARNING,
                            related_entity="Finance",
                            source_claim=claim.claim_text,
                            authoritative_finding="No matching approved Finance record",
                        )
                    )
            else:
                updated.independently_verified = False
                updated.verification_note = (
                    "Approval claim could not be independently verified."
                )
                issues.append(
                    ValidationIssue(
                        code="UNVERIFIED_APPROVAL_CLAIM",
                        message=updated.verification_note,
                        severity=ValidationSeverity.WARNING,
                        related_entity=claim.approver_role_or_name,
                        source_claim=claim.claim_text,
                    )
                )
            verified_claims.append(updated)

        people_count = 0
        if primary_team:
            people_count = len(self.store.team_members(primary_team["id"]))

        has_blocking = any(
            i.severity in (ValidationSeverity.CONFLICT, ValidationSeverity.ERROR)
            for i in conflicts + issues
        )
        # Unverified approval alone should not block planning — it forces human approval.
        confidence = req.confidence
        if conflicts:
            confidence = min(confidence, 0.35)
        elif issues:
            confidence = min(confidence, 0.6)

        result = ValidationResult(
            verified_entities=verified,
            issues=issues,
            conflicts=conflicts,
            ambiguities=ambiguities,
            claimed_vs_verified_approvals=verified_claims,
            confidence=confidence,
            is_safe_to_plan=not has_blocking,
            people_impacted_count=people_count,
        )

        for c in conflicts:
            append_audit(
                case,
                AuditEventType.CONFLICT_DETECTED,
                c.message,
                status=c.severity.value,
                metadata={"code": c.code},
            )

        case.validation = result
        case.status = (
            CaseStatus.VALIDATED if result.is_safe_to_plan else CaseStatus.NEEDS_REVIEW
        )
        append_audit(
            case,
            AuditEventType.ENTITY_VALIDATED,
            (
                "Validation complete. "
                + (
                    "Safe to generate execution plan."
                    if result.is_safe_to_plan
                    else "Blocking issues require human review before/at approval."
                )
            ),
            status="ok" if result.is_safe_to_plan else "needs_review",
            metadata={
                "conflicts": len(conflicts),
                "issues": len(issues),
                "people_impacted": people_count,
            },
        )
        return result
