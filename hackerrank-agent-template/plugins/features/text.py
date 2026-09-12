from __future__ import annotations

from typing import Any, List, Optional

from core.contracts import ExecutionContext
from core.plugin import Plugin

_URGENT_HIGH = {"urgent", "immediately", "asap", "emergency", "right now", "today", "critical", "now"}
_URGENT_MED = {"soon", "as soon as possible", "please", "quickly", "need"}
_NEGATIVE = {"broken", "fail", "failed", "refund", "error", "terrible", "worst", "scam", "fraud", "angry", "unacceptable"}
_POSITIVE = {"thanks", "thank", "great", "love", "awesome", "helpful", "good", "happy"}


def _words(text: str) -> List[str]:
    return [w for w in text.lower().split() if w]


class TextFeatures(Plugin):
    category = "features"
    name = "features.text"
    version = "0.1.0"
    abstract = False
    provides = ["features.text"]
    requires = []
    config_schema = {"text_fields": "list"}

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        fields = ctx.normalized.fields or ctx.item.fields
        text_fields: List[str] = self.config.get("text_fields", [])
        texts = [str(fields[k]) for k in (text_fields or self._candidates(fields)) if fields.get(k)]
        if not texts:
            ctx.features.signals.update(self._empty_signals())
            return ctx
        text = " ".join(texts)
        signals = self._signals(text)
        ctx.features.signals.update({f"text.{k}": self._sig(v, "text") for k, v in signals.items()})
        return ctx

    @staticmethod
    def _candidates(fields) -> List[str]:
        for key in ("text", "message", "ticket", "body", "description", "content"):
            if fields.get(key):
                return [key]
        return list(fields)

    @staticmethod
    def _sig(value: Any, provenance: str) -> dict:
        return {"value": value, "provenance": provenance, "type": type(value).__name__}

    @staticmethod
    def _empty_signals() -> dict:
        base = {"text_length": 0, "word_count": 0, "sentence_count": 0, "uppercase_ratio": 0.0, "exclaim_count": 0}
        urgency = "low"
        return {f"text.{k}": TextFeatures._sig(v, "text") for k, v in base.items()} | {
            "text.urgency": TextFeatures._sig(urgency, "text")
        }

    @staticmethod
    def _signals(text: str) -> dict:
        words = _words(text)
        sentences = [s for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        uppercase = sum(1 for ch in text if ch.isupper())
        length = max(1, len(text))
        low = text.lower()
        count = lambda keys: sum(low.count(k) for k in keys)
        urgency = "high" if (count(_URGENT_HIGH) > 0 or text.count("!") >= 2) else ("medium" if count(_URGENT_MED) > 0 else "low")
        sentiment = "positive" if count(_POSITIVE) > count(_NEGATIVE) else ("negative" if count(_NEGATIVE) > 0 else "neutral")
        return {
            "text_length": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "uppercase_ratio": round(uppercase / length, 3),
            "exclaim_count": text.count("!"),
            "urgency": urgency,
            "sentiment": sentiment,
        }