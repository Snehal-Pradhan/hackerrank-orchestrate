from __future__ import annotations

from core.contracts import ExecutionContext
from core.plugin import Plugin


class ConfidenceBand(Plugin):
    category = "confidence"
    name = "confidence.band"
    version = "0.1.0"
    abstract = False
    provides = ["confidence.band"]
    requires = []
    config_schema = {
        "auto_min": float,
        "log_min": float,
        "escalate_below": float,
    }

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        decision = ctx.decision
        if decision is None:
            ctx.confidence.score = 0.0
            ctx.confidence.band = "escalate"
            return ctx
        rule = decision.rule_fired or ""
        if rule.startswith("risk.") or rule.startswith("fallback.") or decision.label == "BLOCK":
            score, band, basis = 0.98, "auto", "safety or fallback rule"
        elif decision.label == "ESCALATE":
            score, band, basis = 0.85, "auto", f"escalation rule {rule}"
        else:
            score, band, basis = 0.6, "log", f"domain rule {rule}"
        escalate_below = self.config.get("escalate_below", 0.5)
        if score < escalate_below and decision.label != "BLOCK":
            decision.label = "ESCALATE"
            decision.reason = f"low confidence ({score:.2f}); escalating"
            decision.rule_fired = f"{rule}->confidence-gate"
            band = "escalate"
        ctx.confidence.score = score
        ctx.confidence.band = band
        ctx.confidence.basis = basis
        return ctx