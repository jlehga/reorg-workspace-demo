"""Integration adapters for simulated enterprise systems."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.data.store import EnterpriseStore
from app.models.plan import PlannedAction


class SystemAdapter(ABC):
    system_name: str

    def __init__(self, store: EnterpriseStore) -> None:
        self.store = store

    @abstractmethod
    def execute(self, action: PlannedAction) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def observe(self, team_id: str) -> dict[str, Any]:
        raise NotImplementedError


class DirectoryAdapter(SystemAdapter):
    system_name = "Directory"

    def execute(self, action: PlannedAction) -> dict[str, Any]:
        team_id = action.payload.get("team_id")
        if team_id not in self.store.teams:
            raise RuntimeError(f"Team {team_id} not found during precondition check")
        return {"preconditions": "ok", "team_id": team_id}

    def observe(self, team_id: str) -> dict[str, Any]:
        team = self.store.teams.get(team_id)
        return {"exists": team is not None}


class HRISAdapter(SystemAdapter):
    system_name = "HRIS"

    def execute(self, action: PlannedAction) -> dict[str, Any]:
        team_id = action.payload["team_id"]
        to_manager_id = action.payload.get("to_manager_id")
        team = self.store.teams[team_id]
        if to_manager_id:
            # Move team org under Jane's org when Jane is receiver
            mgr = self.store.employees[to_manager_id]
            # Prefer org led by this manager if present
            target_org = next(
                (o for o in self.store.orgs.values() if o["leader_id"] == to_manager_id),
                None,
            )
            if target_org:
                team["org_id"] = target_org["id"]
            # Update members' org (except exceptions handled below)
            exception_names = {
                e["person_name"].lower()
                for e in action.payload.get("exceptions", [])
            }
            for eid in list(team["member_ids"]):
                emp = self.store.employees[eid]
                if emp["name"].lower() in exception_names:
                    continue
                emp["org_id"] = team["org_id"]
                # manager of team members stays team manager; team manager reports up
            # Point team manager's manager to new org leader
            team_mgr = self.store.employees[team["manager_id"]]
            team_mgr["manager_id"] = to_manager_id
            team_mgr["org_id"] = team["org_id"]

        # Apply exceptions
        for exc in action.payload.get("exceptions", []):
            person = self.store.find_employee_by_name(exc["person_name"])
            if not person:
                continue
            if person["id"] in team["member_ids"]:
                team["member_ids"].remove(person["id"])
            if exc.get("to_manager"):
                new_mgr = self.store.find_employee_by_name(exc["to_manager"])
                if new_mgr:
                    person["manager_id"] = new_mgr["id"]
                    person["org_id"] = new_mgr["org_id"]
                    person["team_id"] = None
                    # Platform cost center for demo
                    if new_mgr["org_id"] == "ORG-PLATFORM":
                        person["cost_center"] = "CC-4200"
            elif exc.get("to_org_or_manager"):
                # try as org name then person
                org = next(
                    (
                        o
                        for o in self.store.orgs.values()
                        if exc["to_org_or_manager"].lower() in o["name"].lower()
                    ),
                    None,
                )
                if org:
                    person["org_id"] = org["id"]
                    person["manager_id"] = org["leader_id"]
                    person["team_id"] = None
                    if org["id"] == "ORG-PLATFORM":
                        person["cost_center"] = "CC-4200"

        leader_name = None
        if to_manager_id:
            leader_name = self.store.employees[to_manager_id]["name"]
        return {
            "team_id": team_id,
            "org_id": team["org_id"],
            "org_leader": leader_name,
            "member_count": len(team["member_ids"]),
        }

    def observe(self, team_id: str) -> dict[str, Any]:
        team = self.store.teams[team_id]
        org = self.store.orgs[team["org_id"]]
        leader = self.store.employees[org["leader_id"]]
        return {
            "org_leader": leader["name"],
            "org_id": org["id"],
            "member_count": len(team["member_ids"]),
            "team_id": team_id,
        }


class HeadcountAdapter(SystemAdapter):
    system_name = "Headcount Planning"

    def execute(self, action: PlannedAction) -> dict[str, Any]:
        team_id = action.payload["team_id"]
        cc = action.payload["cost_center"]
        plan = self.store.headcount_plan[team_id]
        plan["cost_center"] = cc
        team = self.store.teams[team_id]
        plan["org_id"] = team["org_id"]
        plan["headcount"] = len(team["member_ids"])
        return {"team_id": team_id, "cost_center": cc, "headcount": plan["headcount"]}

    def observe(self, team_id: str) -> dict[str, Any]:
        return dict(self.store.headcount_plan[team_id])


class CostAllocationAdapter(SystemAdapter):
    system_name = "Cost Allocation"

    def execute(self, action: PlannedAction) -> dict[str, Any]:
        team_id = action.payload["team_id"]
        cc = action.payload["cost_center"]
        self.store.cost_allocation[team_id]["cost_center"] = cc
        return {"team_id": team_id, "cost_center": cc}

    def observe(self, team_id: str) -> dict[str, Any]:
        return dict(self.store.cost_allocation[team_id])


class GLMappingAdapter(SystemAdapter):
    """
    No-API system. execute() does not mutate — human task completion does.
    """

    system_name = "GL Mapping"

    def execute(self, action: PlannedAction) -> dict[str, Any]:
        # Intentionally no mutation — returns instructions for human actuator
        return {
            "requires_human": True,
            "instructions": action.payload,
            "current_state": self.observe(action.payload["team_id"]),
        }

    def apply_human_entry(
        self,
        team_id: str,
        new_cost_center: str,
        *,
        force_incorrect: bool = False,
        incorrect_value: str | None = None,
    ) -> dict[str, Any]:
        """Called when Finance Ops marks the manual task complete."""
        value = incorrect_value if force_incorrect else new_cost_center
        if value not in self.store.cost_centers:
            raise RuntimeError(f"Cannot map GL to unknown cost center {value}")
        gl_account = self.store.cost_centers[value]["gl_account"]
        self.store.gl_mapping[team_id] = {
            "team_id": team_id,
            "cost_center": value,
            "gl_account": gl_account,
        }
        return dict(self.store.gl_mapping[team_id])

    def observe(self, team_id: str) -> dict[str, Any]:
        return dict(self.store.gl_mapping[team_id])


class ReportingAdapter(SystemAdapter):
    system_name = "Reporting"

    def execute(self, action: PlannedAction) -> dict[str, Any]:
        team_id = action.payload["team_id"]
        # Only sync if not blocked
        if self.store.reporting.get("blocked"):
            raise RuntimeError(
                self.store.reporting.get("block_reason")
                or "Reporting propagation blocked"
            )
        self.store.reporting["last_synced_from_gl"][team_id] = dict(
            self.store.gl_mapping[team_id]
        )
        return {"synced": True, "team_id": team_id}

    def block(self, reason: str) -> None:
        self.store.reporting["blocked"] = True
        self.store.reporting["block_reason"] = reason

    def unblock(self) -> None:
        self.store.reporting["blocked"] = False
        self.store.reporting["block_reason"] = None

    def observe(self, team_id: str) -> dict[str, Any]:
        synced = self.store.reporting["last_synced_from_gl"].get(team_id, {})
        return {
            "synced_cost_center": synced.get("cost_center"),
            "blocked": self.store.reporting.get("blocked", False),
            "block_reason": self.store.reporting.get("block_reason"),
        }


def build_adapters(store: EnterpriseStore) -> dict[str, SystemAdapter]:
    return {
        "Directory": DirectoryAdapter(store),
        "HRIS": HRISAdapter(store),
        "Headcount Planning": HeadcountAdapter(store),
        "Cost Allocation": CostAllocationAdapter(store),
        "GL Mapping": GLMappingAdapter(store),
        "Reporting": ReportingAdapter(store),
    }
