from __future__ import annotations

from typing import Any, Dict, List

import plugins
from .contracts import OutputRow
from .pipeline import Pipeline
from .recipe import Recipe
from .registry import Registry

CORE_STAGES_FOR_GOLD = {"output_row_id": "row_id", "output_decision": "columns.decision"}


def build_registry() -> Registry:
    return Registry().discover(plugins)


def _pick(registry: Registry, capability: str, spec: Dict[str, Any]):
    name = spec.get("plugin")
    config = spec.get("config", {})
    if name:
        plugin_cls = registry.get(name)
    else:
        matches = registry.by_capability(capability)
        if not matches:
            raise ValueError(f"no plugin provides {capability!r}")
        plugin_cls = matches[0]
    instance = plugin_cls(config)
    instance.bind(registry)
    return instance


def run_pipeline(recipe_path: str, input_path: str, output_path: str, trace_path: str = "") -> Dict[str, Any]:
    recipe = Recipe.load(recipe_path)
    io = recipe.get("io", {})
    registry = build_registry()

    loader = _pick(registry, "input.csv", io.get("input", {}))
    pipeline = Pipeline(registry, recipe)
    pipeline.setup()
    try:
        items = loader.load(input_path)
        t0 = 0.0
        import time

        t0 = time.perf_counter()
        contexts = [pipeline.process_item(item) for item in items]
        elapsed = time.perf_counter() - t0
        rows: List[OutputRow] = [ctx.output_row for ctx in contexts if ctx.output_row is not None]

        writer = _pick(registry, "output.csv", io.get("output", {}))
        writer.write(rows, output_path)

        quarantined = [ctx for ctx in contexts if ctx.validation and not ctx.validation.ok]
        stats = {
            "recipe": recipe["name"],
            "items": len(items),
            "rows": len(rows),
            "quarantined": len(quarantined),
            "elapsed_s": round(elapsed, 3),
        }
        if trace_path:
            _write_trace(contexts, trace_path)
        return stats
    finally:
        pipeline.shutdown()


def _write_trace(contexts, trace_path: str) -> None:
    import json

    with open(trace_path, "w", encoding="utf-8") as fh:
        for ctx in contexts:
            fh.write(json.dumps(ctx.model_dump()) + "\n")


def evaluate(gold_path: str, rows: List[OutputRow]) -> Dict[str, Any]:
    import csv

    gold: Dict[str, str] = {}
    with open(gold_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            gold[row["row_id"]] = row["decision"]

    correct = 0
    compared = 0
    details: List[Dict[str, Any]] = []
    for row in rows:
        expected = gold.get(row.row_id)
        if expected is None:
            continue
        compared += 1
        got = row.columns.get("decision")
        ok = got == expected
        correct += int(ok)
        details.append({"row_id": row.row_id, "expected": expected, "got": got, "ok": ok})
    accuracy = correct / compared if compared else 0.0
    return {"compared": compared, "correct": correct, "accuracy": round(accuracy, 4), "details": details}