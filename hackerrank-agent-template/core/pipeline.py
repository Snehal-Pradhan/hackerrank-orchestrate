from __future__ import annotations

import time
from typing import Any, Dict, Iterator, List, Optional

from .contracts import ExecutionContext, Item, OutputRow
from .plugin import Plugin
from .registry import Registry

STAGES = [
    "clean",
    "context",
    "retrieve",
    "extract",
    "perceive",
    "decide",
    "confidence",
    "validate",
    "trace",
    "output",
]

SKIPPED_WHEN_ABORTED = {"validate", "output"}


class Stage:
    def __init__(self, name: str, spec: Dict[str, Any], registry: Registry) -> None:
        self.name = name
        self.mode = spec.get("mode", "none")
        self.plugins: List[Plugin] = []
        for entry in spec.get("plugins", []):
            plugin_name = entry["name"]
            self.plugins.append(registry.instantiate(plugin_name, entry.get("config", {})))


class Pipeline:
    def __init__(self, registry: Registry, recipe: Dict[str, Any]) -> None:
        self.registry = registry
        self.recipe = recipe
        stage_specs = recipe.get("stages", {})
        self.stages = [Stage(name, stage_specs.get(name, {}), registry) for name in STAGES]

    def setup(self) -> None:
        for stage in self.stages:
            for plugin in stage.plugins:
                plugin.setup()

    def shutdown(self) -> None:
        for stage in self.stages:
            for plugin in stage.plugins:
                plugin.shutdown()

    def process_item(self, item: Item) -> ExecutionContext:
        ctx = ExecutionContext(item=item)
        for stage in self.stages:
            if ctx.aborted and stage.name not in SKIPPED_WHEN_ABORTED:
                continue
            if not stage.plugins or stage.mode in ("none", None):
                continue
            self._run_stage(stage, ctx)
        self._finalize(ctx)
        return ctx

    def _run_stage(self, stage: Stage, ctx: ExecutionContext) -> None:
        if stage.mode == "list":
            for plugin in stage.plugins:
                self._invoke(plugin, ctx, stage.name)
        elif stage.mode == "chain":
            for plugin in stage.plugins:
                try:
                    if plugin.can_handle(ctx):
                        self._invoke(plugin, ctx, stage.name)
                        break
                except Exception:
                    continue
        else:
            plugin = stage.plugins[0]
            self._invoke(plugin, ctx, stage.name)

    def _invoke(self, plugin: Plugin, ctx: ExecutionContext, stage: str) -> None:
        start = time.perf_counter()
        plugin.process(ctx)
        elapsed = (time.perf_counter() - start) * 1000.0
        ctx.add_trace(
            stage=stage,
            plugin=plugin.name,
            version=plugin.version,
            time_ms=round(elapsed, 3),
            detail={"mode": getattr(plugin, "actor", False)},
        )

    def _finalize(self, ctx: ExecutionContext) -> None:
        decision = ctx.decision
        if ctx.output_row is None:
            ctx.output_row = OutputRow(row_id=ctx.item.row_id if ctx.item else "0")
        ctx.output_row.columns = {"decision": decision.label if decision else "ERROR"}

    @staticmethod
    def process_many(pipeline: "Pipeline", items: Iterator[Item]) -> List[ExecutionContext]:
        return [pipeline.process_item(item) for item in items]