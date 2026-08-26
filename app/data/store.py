"""In-memory enterprise data repositories backed by JSON fixtures."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent


class EnterpriseStore:
    """
    Simulated systems of record.

    Domain systems remain authoritative for their data. The Reorg Case is
    authoritative only for workflow execution state.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or DATA_DIR
        self._load()

    def _load(self) -> None:
        employees = json.loads((self.data_dir / "employees.json").read_text())
        orgs = json.loads((self.data_dir / "orgs.json").read_text())
        cost_centers = json.loads((self.data_dir / "cost_centers.json").read_text())
        approvals = json.loads((self.data_dir / "approvals.json").read_text())

        self.employees: dict[str, dict[str, Any]] = {
            e["id"]: copy.deepcopy(e) for e in employees["employees"]
        }
        self.employees_by_name: dict[str, dict[str, Any]] = {
            e["name"].lower(): e for e in self.employees.values()
        }
        self.orgs: dict[str, dict[str, Any]] = {
            o["id"]: copy.deepcopy(o) for o in orgs["orgs"]
        }
        self.teams: dict[str, dict[str, Any]] = {
            t["id"]: copy.deepcopy(t) for t in orgs["teams"]
        }
        self.teams_by_name: dict[str, dict[str, Any]] = {
            t["name"].lower(): t for t in self.teams.values()
        }
        self.cost_centers: dict[str, dict[str, Any]] = {
            c["id"]: copy.deepcopy(c) for c in cost_centers["cost_centers"]
        }
        self.approvals: list[dict[str, Any]] = copy.deepcopy(approvals["approvals"])

        # Simulated downstream state
        self.headcount_plan: dict[str, Any] = {
            t["id"]: {
                "team_id": t["id"],
                "cost_center": t["cost_center"],
                "headcount": len(t["member_ids"]),
                "org_id": t["org_id"],
            }
            for t in self.teams.values()
        }
        self.cost_allocation: dict[str, Any] = {
            t["id"]: {"team_id": t["id"], "cost_center": t["cost_center"]}
            for t in self.teams.values()
        }
        # GL has no API — state is updated only via human task completion
        self.gl_mapping: dict[str, Any] = {
            t["id"]: {
                "team_id": t["id"],
                "cost_center": t["cost_center"],
                "gl_account": self.cost_centers[t["cost_center"]]["gl_account"],
            }
            for t in self.teams.values()
        }
        self.reporting: dict[str, Any] = {
            "last_synced_from_gl": copy.deepcopy(self.gl_mapping),
            "blocked": False,
            "block_reason": None,
        }

    def reset(self) -> None:
        self._load()

    def find_employee_by_name(self, name: str) -> Optional[dict[str, Any]]:
        return self.employees_by_name.get(name.strip().lower())

    def find_team_by_name(self, name: str) -> Optional[dict[str, Any]]:
        key = name.strip().lower()
        if key in self.teams_by_name:
            return self.teams_by_name[key]
        # fuzzy contains
        for tname, team in self.teams_by_name.items():
            if key in tname or tname in key:
                return team
        return None

    def team_members(self, team_id: str) -> list[dict[str, Any]]:
        team = self.teams[team_id]
        return [self.employees[eid] for eid in team["member_ids"] if eid in self.employees]

    def find_finance_approval(
        self, cost_centers: list[str], subject_keywords: list[str]
    ) -> Optional[dict[str, Any]]:
        for apr in self.approvals:
            if apr["approver_role"].lower() != "finance":
                continue
            if apr["status"] != "approved":
                continue
            related = set(apr.get("related_cost_centers", []))
            if related.intersection(cost_centers):
                subject = apr.get("subject", "").lower()
                if any(k.lower() in subject for k in subject_keywords):
                    return apr
        return None


# Process-wide demo store (Streamlit session may hold its own copy)
_DEFAULT_STORE: EnterpriseStore | None = None


def get_store() -> EnterpriseStore:
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = EnterpriseStore()
    return _DEFAULT_STORE


def fresh_store() -> EnterpriseStore:
    return EnterpriseStore()
