# Reorg Case: Agentic-Driven Reorganization Prototype

A functional take-home prototype that turns **unstructured reorg intent** into a governed **Reorg Case**: interpret → validate → plan → approve → execute (automated + manual) → reconcile → audit.

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

## Running locally

Copy-paste guide (email-friendly): **[RUN.txt](RUN.txt)**. Submission checklist: **[SUBMISSION.txt](SUBMISSION.txt)**.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8765
```

Or: `./run_demo.sh`

Open [http://127.0.0.1:8765](http://127.0.0.1:8765).

Demo login: **ops.demo** / **reorg-demo** (see RUN.txt).

`OPENAI_API_KEY` is optional. Without it, a deterministic demo extractor drives the scenarios.

### Tests

```bash
source .venv/bin/activate
pytest -q
```

---

## Demo scenario (60 seconds)

See **[RUN.txt](RUN.txt)** for the short path. Summary: Scenario A → Analyze → note unverified Finance → Approve → Run → Mark Complete GL → Reconciliation. Optional: incorrect-GL failure beat or Scenario B.

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
