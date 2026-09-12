from __future__ import annotations

from typing import Optional

from core.contracts import Decision, ExecutionContext
from .level import LevelPlugin


class Fallback(LevelPlugin):
    name = "policy.fallback"
    version = "0.1.0"
    abstract = False
    provides = ["policy.fallback"]
    requires = []
    config_schema = {"default_label": str, "reason": str}

    def decide(self, ctx: ExecutionContext) -> Optional[Decision]:
        return Decision(
            label=self.config.get("default_label", "ESCALATE"),
            reason=self.config.get("reason", "no rule fired; safest action"),
            rule_fired="fallback.safest-action",
            is_fallback=True,
        )