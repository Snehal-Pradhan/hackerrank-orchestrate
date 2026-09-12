from __future__ import annotations

from core.contracts import Decision, ExecutionContext
from plugins.validation.output_contract import OutputContract


def _ctx(label):
    ctx = ExecutionContext(item=None)
    ctx.decision = Decision(label=label, reason="x", rule_fired="r")
    return ctx


def test_allows_membership():
    ctx = _ctx("RESPOND")
    OutputContract({"allowed_labels": ["RESPOND", "ESCALATE", "BLOCK"]}).process(ctx)
    assert ctx.validation.ok is True
    assert ctx.validation.errors == []


def test_rejects_outside_membership():
    ctx = _ctx("MUTE")
    OutputContract({"allowed_labels": ["RESPOND", "ESCALATE", "BLOCK"]}).process(ctx)
    assert ctx.validation.ok is False
    assert any("MUTE" in error for error in ctx.validation.errors)


def test_missing_decision_fails():
    ctx = ExecutionContext(item=None)
    OutputContract({"allowed_labels": ["RESPOND", "ESCALATE"]}).process(ctx)
    assert ctx.validation.ok is False
    assert "no decision produced" in ctx.validation.errors