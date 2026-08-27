# Reorg Workspace: Agentic-Driven Reorganization Prototype

A functional take-home prototype. **Reorg Workspace** is the operator portal; each governed **Reorg Case** turns unstructured reorg intent into interpret → validate → plan → approve → execute (automated + manual) → reconcile → audit.

It is designed for HR, FP&A, Finance, Legal, and Operations stakeholders as much as for engineers. The product should feel **agentic on the inside, simple on the outside**.

**Design principle:** Agents interpret and plan. Policies authorize. Tools execute. Humans resolve ambiguity and high-impact decisions. The system verifies the result.

Full design rationale: [`docs/design.md`](docs/design.md).

---

## Architecture

```text
Freeform input
     → LLM / structured extraction (schema-validated)
     → Authoritative-system validation (deterministic)
     → Dependency-aware plan
     → Deterministic approval policy
     → Adapters (HRIS, Headcount, Cost Allocation)
     → Human task for no-API GL mapping
     → Reporting
     → Reconciliation (expected vs observed)
```

The **Reorg Case** is the system of record for *execution*. HRIS/Finance/planning systems remain authoritative for their underlying data.

---

## Try it

1. **Live demo (primary):** https://jlehga-reorg-workspace-demo-app-ggbknu.streamlit.app/  
   Login: **demouser** / **test123**
2. **Design deliverable:** [docs/design.md](docs/design.md)
3. **Source (version-controlled):** private repo
   [jlehga/reorg-execution-system](https://github.com/jlehga/reorg-execution-system) —
   access on request, or use an attached / release zip. Cloning is not required
   to review the design or walkthrough.
4. **OPTIONAL** — only if the live link does not work: zip (preferred) or clone
   if access has been granted — see [RUN.txt](RUN.txt) and
   [docs/HOSTING.md](docs/HOSTING.md).

Copy-paste guide: **[RUN.txt](RUN.txt)**. Submission checklist: **[SUBMISSION.txt](SUBMISSION.txt)**.

### Running locally (fallback)

From a zip (or clone if access granted):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8765
```

Or: `./run_demo.sh`

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). After Sign in: Workspace home → New Reorg Case → case workflow.

Optional `LLM_API_KEY`: lets the app call a live LLM to interpret freeform reorg
text into a structured case. Without it, a built-in deterministic parser runs the
demo. Optional: `LLM_MODEL`, `LLM_BASE_URL`. The model is not used for approvals
or system writes.

### Tests

```bash
source .venv/bin/activate
pytest -q
```

---

## Demo scenario (60 seconds)

See **[RUN.txt](RUN.txt)** for the short path. Summary: Sign in → Workspace home → New Reorg Case → Analyze → note unverified Finance → Approve → Run → Mark Complete GL → Reconciliation. Optional: incorrect-GL failure beat or Scenario B.

---

## Repository structure

```text
app.py                 # Streamlit entrypoint
run_demo.sh            # venv + streamlit on :8765
RUN.txt / SUBMISSION.txt
app/
  agents/              # Interpretation + LLM provider abstraction
  models/              # Typed Reorg Case domain models
  services/            # Validation, planning, execution, reconciliation
  policies/            # Deterministic approval gate
  integrations/        # Simulated system adapters (incl. manual GL)
  workflow/            # Facade used by UI/tests
  data/                # Fixtures + scenarios
  ui/                  # Presentational Streamlit helpers
  utils/               # Audit + PII helpers
docs/design.md
tests/
requirements.txt
```

---

## Prototype scope

**In scope:** two meaningful slices: (A) interpretation + authoritative validation, (B) dependency-aware planning, approval, mixed execution, reconciliation, plus auditability and a demo-friendly UI.

**Out of scope:** production integrations, real auth/RBAC, durable workflow infra, Slack/email ingestion, compensation workflows, and production observability. See design doc §15 for the explicit non-build list and rationale.

---

## Design document

See **[docs/design.md](docs/design.md)** for goals/non-goals, architecture, risks, alternatives, AI usage/overrides, and next steps.
