from __future__ import annotations

from typing import Optional

from core.contracts import Decision, ExecutionContext
from .level import LevelPlugin

_TRIGGERS = ("risk.scam", "risk.injection", "risk.pii_card")


class SafetyGate(LevelPlugin):
    name = "policy.safety"
    version = "0.1.0"
    abstract = False
    provides = ["policy.safety"]
    requires = ["features.risk"]
    config_schema = {"block_label": str}

    def decide(self, ctx: ExecutionContext) -> Optional[Decision]:
        for key in _TRIGGERS:
            signal = ctx.features.signals.get(key)
            if signal and signal.get("value") is True:
                ctx.aborted = True
                ctx.abort_reason = f"safety triggered by {key}"
                return Decision(
                    label=self.config.get("block_label", "BLOCK"),
                    reason=f"blocked by safety gate ({key})",
                    rule_fired=key,
                )
        return None