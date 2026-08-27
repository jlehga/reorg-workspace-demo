# Rubric checklist vs take-home requirements

| Assignment requirement | Design | Prototype demonstration | Intentionally non-goal? |
| --- | --- | --- | --- |
| Design doc: summary / outcome | `docs/design.md` §1 | README + live case narrative | — |
| Goals and non-goals | §3–4, §15 | Sidebar scenarios + README scope | — |
| Approach: capture → validation → propagation; components; agentic blocks; HITL | §6–10 | UI tabs 1–5; `ReorgWorkflow` | — |
| Alternatives considered | §12 | Discussed in design (not UI) | — |
| Risks / failure modes + blast radius + detection | §13 | Scenario B; incorrect GL checkbox | — |
| Assumptions and open questions | §14 | Design doc | — |
| Functional prototype of 1–2 key slices | §15 | Slice A (interpret/validate) + Slice B (plan/execute/reconcile) | — |
| Freeform text intake (no structured event) | §8 Capture | Submit tab textarea | Real Slack/email ingestion out of scope |
| ≥1 system with no API → human keys change | §10; HumanTask | GL Mapping manual task + Mark Complete | — |
| Data includes compensation / PII | §11 | Prompt redaction + audit minimization | Full DLP/RBAC out of scope |
| Human approval before downstream moves | §10; `ApprovalPolicy` | Plan & Approve tab | Production identity out of scope |
| Ambiguity: state assumption, keep going | §14–16 | Assumptions list on case; Scenario B | — |
| Explicit scoping (“chose not to build X”) | §4, §15 | README + design | — |
| Reasoning over single “correct” answer | Whole doc | Tradeoffs in §12 | — |
| Ready to show where AI shaped vs overridden | §16 | Design §16 | — |
| Order of operations critical / codified | §8–9; `depends_on` | Plan tab dependency list; dependency-block test | — |
| No single SoR today → Reorg Case as execution SoR | §7 | Case id + audit + reconciliation | Domain SoRs remain authoritative |
| Errors surface weeks later → detect earlier | §13; reconciliation | Reconciliation tab; reporting blocked on GL fail | — |

Interview logistics assets (Meet prep, NDA, no AI note-taking during interview) are process constraints for the candidate, not product requirements—no code changes required.
