"""Demo scenario freeform texts and helpers."""

from __future__ import annotations

SCENARIO_A_SUCCESS = """\
Effective September 1, 2026, move the Payments Engineering team from Mike Chen's \
organization to Jane Smith. The 14 team members should move from cost center \
CC-4102 to CC-4175. Sarah Patel will instead move to Platform under David Kim. \
Finance has approved the budget impact.
"""

SCENARIO_B_FAILURE = """\
Effective October 15, 2026, move Payments Engineering from Mike Chen to Jane Smith. \
All 20 engineers should move to cost center CC-9999. Finance already signed off. \
Also move the Ledger team under an unknown manager named Alex Unknown.
"""

SCENARIOS = {
    "scenario_a_success": {
        "label": "Scenario A — Payments move (mostly valid, claimed Finance approval)",
        "text": SCENARIO_A_SUCCESS.strip(),
        "notes": (
            "Valid entities and cost centers. Headcount claim (14) matches. "
            "Finance approval is claimed in text but NOT recorded in the approval system. "
            "Sarah Patel exception is valid. Demo: approve, execute, complete GL correctly."
        ),
    },
    "scenario_b_failure": {
        "label": "Scenario B — Ambiguity / invalid cost center / headcount mismatch",
        "text": SCENARIO_B_FAILURE.strip(),
        "notes": (
            "Headcount claim (20) does not match Payments membership (14). "
            "CC-9999 exists but is inactive. Alex Unknown does not exist. "
            "Finance approval claimed but unverified. Demonstrates governed failure handling."
        ),
    },
}
