from __future__ import annotations

from typing import Any, Dict, List

from core.contracts import Decision, ExecutionContext
from core.plugin import Plugin


class Cascade(Plugin):
    category = "policy"
    name = "policy.cascade"
    version = "0.1.0"
    abstract = False
    provides = ["policy.cascade"]
    requires = []
    config_schema = {"levels": "list of level plugin configs", "traced_level": bool}

    def setup(self) -> None:
        self._levels: List[object] = []
        for entry in self.config.get("levels", []):
            name = entry["name"]
            instance = self.registry.instantiate(name, entry.get("config", {}))
            instance.setup()
            self._levels.append(instance)

    def shutdown(self) -> None:
        for level in self._levels:
            level.shutdown()

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        for level in self._levels:
            decision: Decision = level.decide(ctx)
            if decision is not None:
                ctx.decision = decision
                if self.config.get("traced_level", True):
                    ctx.context.truncation_log.append(f"level_decision={decision.rule_fired}")
                break
            if ctx.aborted:
                break
        return ctx