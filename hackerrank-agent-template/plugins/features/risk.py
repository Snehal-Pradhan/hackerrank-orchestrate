from __future__ import annotations

import re
from typing import List

from core.contracts import ExecutionContext
from core.plugin import Plugin

_SCAM_KEYWORDS = [
    "transfer", "win", "prize", "verify account", "urgent payment", "bitcoin", "gift card",
    "inheritance", "password", "otp", "wire", "lottery", "nigerian prince", "claim the gift",
]
_INJECTION_KEYWORDS = [
    "ignore previous", "disregard", "system prompt", "forget your", "dupa instructions",
    "override your instructions", "ignore all instructions", "repeat after me", "<system>",
]
_PII_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_PII_PHONE = re.compile(r"(\+?\d[\d\s\-()]{7,}\d)")
_PII_CARD = re.compile(r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}")


class RiskFeatures(Plugin):
    category = "features"
    name = "features.risk"
    version = "0.1.0"
    abstract = False
    provides = ["features.risk"]
    requires = []
    config_schema = {
        "text_fields": "list",
        "min_scam_signals": int,
        "min_injection_signals": int,
    }

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        fields = ctx.normalized.fields or ctx.item.fields
        texts: List[str] = []
        text_fields = self.config.get("text_fields", [])
        keys = text_fields or list(fields)
        for key in keys:
            value = fields.get(key)
            if isinstance(value, str):
                texts.append(value)
        if not texts:
            return ctx
        text = " ".join(texts).lower()
        scam_count = sum(1 for k in _SCAM_KEYWORDS if k in text)
        injection_count = sum(1 for k in _INJECTION_KEYWORDS if k in text)
        min_scam = int(self.config.get("min_scam_signals", 2))
        min_injection = int(self.config.get("min_injection_signals", 1))
        signals = {
            "risk.scam": {"value": scam_count >= min_scam, "provenance": "risk", "type": "bool"},
            "risk.scam_hits": {"value": scam_count, "provenance": "risk", "type": "int"},
            "risk.injection": {
                "value": injection_count >= min_injection, "provenance": "risk", "type": "bool"
            },
            "risk.injection_hits": {"value": injection_count, "provenance": "risk", "type": "int"},
            "risk.pii_email": {"value": bool(_PII_EMAIL.search(text)), "provenance": "risk", "type": "bool"},
            "risk.pii_phone": {"value": bool(_PII_PHONE.search(text)), "provenance": "risk", "type": "bool"},
            "risk.pii_card": {"value": bool(_PII_CARD.search(text)), "provenance": "risk", "type": "bool"},
        }
        ctx.features.signals.update(signals)
        return ctx
