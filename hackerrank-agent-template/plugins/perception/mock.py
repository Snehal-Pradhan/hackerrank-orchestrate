from __future__ import annotations

from typing import List

from core.contracts import ExecutionContext
from core.plugin import Plugin

_REFUND = {"refund", "money back", "reimburse"}
_CANCEL = {"cancel", "stop service", "unsubscribe"}
_COMPLAINT = {"broken", "not working", "bug", "error", "failed", "terrible", "worst"}
_HELP = {"help", "how do", "how to", "question", "guide", "tutorial"}
_ALERT = {"urgent", "emergency", "immediately", "asap"}


class MockPerception(Plugin):
    category = "perception"
    name = "perception.mock"
    version = "0.1.0"
    abstract = False
    provides = ["perception.lang"]
    requires = []
    config_schema = {"text_fields": "list"}

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        fields = ctx.normalized.fields or ctx.item.fields
        text_fields: List[str] = self.config.get("text_fields", [])
        keys = text_fields or list(fields)
        text = " ".join(str(fields[k]) for k in keys if fields.get(k)).lower()
        intents: List[str] = []
        if _REFUND & set(text.split()):
            intents.append("refund")
        if _CANCEL & set(_word_set(text)):
            intents.append("cancel")
        if any(k in text for k in _COMPLAINT):
            intents.append("complaint")
        if any(k in text for k in _HELP):
            intents.append("help")
        if any(k in text for k in _ALERT):
            intents.append("alert")
        ctx.perception.provider = "mock"
        ctx.perception.structured = {"intents": intents}
        return ctx


def _word_set(text: str) -> set:
    return {w for w in text.split() if w}