from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from core.contracts import ExecutionContext, Item
from core.registry import Registry

ROOT = Path(__file__).resolve().parents[1]


def run_cascade(registry: Registry, ctx: ExecutionContext, levels: List[dict]) -> None:
    cascade = registry.instantiate("policy.cascade", {"levels": levels})
    cascade.setup()
    cascade.process(ctx)
    cascade.shutdown()


def build_ctx(message: str, registry: Registry) -> ExecutionContext:
    ctx = ExecutionContext(item=Item(row_id="1", fields={"message": message}))
    for name, config in (
        ("cleaning.normalize", {}),
        ("features.text", {"text_fields": ["message"]}),
        ("features.risk", {"text_fields": ["message"]}),
    ):
        plugin = registry.instantiate(name, config)
        plugin.setup()
        plugin.process(ctx)
        plugin.shutdown()
    return ctx