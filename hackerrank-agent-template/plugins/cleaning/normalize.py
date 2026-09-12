from __future__ import annotations

import re
from typing import Any, Dict

from core.contracts import ExecutionContext
from core.plugin import Plugin

_WS = re.compile(r"\s+")


class TextNormalize(Plugin):
    category = "cleaning"
    name = "cleaning.normalize"
    version = "0.1.0"
    abstract = False
    provides = ["cleaning.text"]
    requires = []
    config_schema = {"strip": bool, "collapse_ws": bool, "lower": bool}

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        cleaned: Dict[str, Any] = {}
        for key, value in ctx.item.fields.items():
            if isinstance(value, str):
                value = value.strip() if self.config.get("strip", True) else value
                if self.config.get("collapse_ws", True):
                    value = _WS.sub(" ", value)
                if self.config.get("lower", False):
                    value = value.lower()
            cleaned[key] = value
        ctx.normalized = ctx.normalized.model_copy(update={"fields": cleaned})
        return ctx