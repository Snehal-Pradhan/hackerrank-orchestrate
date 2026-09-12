from __future__ import annotations

from typing import List

from core.contracts import ExecutionContext
from core.plugin import Plugin


class OutputContract(Plugin):
    category = "validation"
    name = "validation.output_contract"
    version = "0.1.0"
    abstract = False
    provides = ["validation.output_contract"]
    requires = []
    config_schema = {"allowed_labels": "list", "columns": "list"}

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        decision = ctx.decision
        errors: List[str] = []
        allowed = self.config.get("allowed_labels", [])
        if decision is None:
            errors.append("no decision produced")
        elif allowed and decision.label not in allowed:
            errors.append(f"decision {decision.label!r} not in allowed {allowed}")
        ctx.validation.errors = errors
        ctx.validation.ok = not errors
        ctx.validation.checks = {
            "allowed_labels": allowed,
            "decision": decision.label if decision else None,
            "rule_fired": decision.rule_fired if decision else None,
        }
        return ctx