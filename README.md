# Reorg Case — Agentic-Driven Reorganization Prototype

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

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8765
```

Open the URL Streamlit prints (default in this guide: [http://127.0.0.1:8765](http://127.0.0.1:8765)).

### Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | No | If set, interpretation uses OpenAI structured JSON extraction. |
| `OPENAI_MODEL` | No | Defaults to `gpt-4o-mini`. |

Without an API key, the app uses a **deterministic demo extractor** that still produces schema-valid `ExtractedRequest` objects for the included scenarios. The provider name is shown in the sidebar so the limitation is explicit—not disguised as a live model.

### Tests

```bash
source .venv/bin/activate
pytest -q
```

---

## Demo scenario

### Scenario A — mostly successful path (default)

1. Sidebar → **Scenario A** → **Load scenario text** (or paste the sample).
2. Click **Analyze Reorg**.
3. **Reorg Case** tab: show effective date, org/CC moves, Sarah Patel exception, and the warning that Finance approval was *claimed* but not independently verified.
4. **Plan & Approve** tab: show dependency graph (approval gate → HRIS → headcount/cost alloc → **manual GL** → reporting → reconcile). Click **Approve Plan**.
5. **Execution** tab → **Run execution**. Automated steps complete; GL mapping pauses as **Needs Human Action**.
6. Review the Finance Operations task instructions → **Mark Complete** (correct `CC-4175`).
7. **Reconciliation** tab: all systems Passed; case **Completed**.
8. **Audit** tab: walk the event trail.

Optional failure beat: check **Simulate incorrect GL entry** before Mark Complete — reconciliation fails, reporting is blocked, case does not complete.

### Scenario B — ambiguity / failure

Load Scenario B. Analysis surfaces headcount mismatch, inactive cost center `CC-9999`, unknown entities, and unverified Finance claims. This demonstrates a governed workflow, not only a happy path.

---

## Repository structure

```text
app.py                 # Streamlit entrypoint
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

**In scope:** two meaningful slices—(A) interpretation + authoritative validation, (B) dependency-aware planning, approval, mixed execution, reconciliation—plus auditability and a demo-friendly UI.

**Out of scope:** production integrations, real auth/RBAC, durable workflow infra, Slack/email ingestion, compensation workflows, and production observability. See design doc §15 for the explicit non-build list and rationale.

---

## Design document

See **[docs/design.md](docs/design.md)** for goals/non-goals, architecture, risks, alternatives, AI usage/overrides, and next steps.
