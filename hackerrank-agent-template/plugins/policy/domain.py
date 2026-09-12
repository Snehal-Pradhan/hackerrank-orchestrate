from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List, Optional

from core.contracts import Decision, ExecutionContext
from .level import LevelPlugin

_OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    "exists": lambda actual, expected: actual is not None,
    "eq": lambda actual, expected: actual == expected,
    "neq": lambda actual, expected: actual != expected,
    "gt": lambda actual, expected: actual is not None and actual > expected,
    "gte": lambda actual, expected: actual is not None and actual >= expected,
    "lt": lambda actual, expected: actual is not None and actual < expected,
    "lte": lambda actual, expected: actual is not None and actual <= expected,
    "in_list": lambda actual, expected: actual in expected,
    "contains": lambda actual, expected: expected in (actual or ""),
}


def _resolve(ctx: ExecutionContext, path: str) -> Any:
    if path.startswith("feature."):
        return ctx.features.signals.get(path[len("feature."):], {}).get("value")
    if path.startswith("field."):
        fields = ctx.normalized.fields or ctx.item.fields
        return fields.get(path[len("field."):])
    if path.startswith("perception."):
        return ctx.perception.structured.get(path[len("perception."):])
    return None


class DomainRules(LevelPlugin):
    name = "policy.domain"
    version = "0.1.0"
    abstract = False
    provides = ["policy.domain"]
    requires = []
    config_schema = {"rules_path": str}

    def setup(self) -> None:
        path = self.config.get("rules_path")
        if not path:
            raise RuntimeError(f"{self.name} requires rules_path")
        if not os.path.exists(path):
            raise FileNotFoundError(f"rules file not found: {path}")
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        self._rules = payload["rules"]

    def decide(self, ctx: ExecutionContext) -> Optional[Decision]:
        for rule in self._rules:
            if self._matches(ctx, rule.get("when", [])):
                return Decision(
                    label=rule["label"],
                    reason=rule.get("reason", f"matched rule {rule['name']}"),
                    rule_fired=rule["name"],
                    is_fallback=False,
                )
        return None

    def _matches(self, ctx: ExecutionContext, conditions: List[Dict[str, Any]]) -> bool:
        if not conditions:
            return True
        for condition in conditions:
            actual = _resolve(ctx, condition["path"])
            op = condition.get("op", "eq")
            expected = condition.get("value")
            if op not in _OPERATORS or not _OPERATORS[op](actual, expected):
                return False
        return True