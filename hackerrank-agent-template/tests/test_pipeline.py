from __future__ import annotations

from core.contracts import ExecutionContext, Item
from core.pipeline import Pipeline
from core.plugin import Plugin
from core.registry import Registry


class StageA(Plugin):
    name = "t.clean.a"
    abstract = False

    def process(self, ctx):
        ctx.context.truncation_log.append("A")
        return ctx


class StageB(Plugin):
    name = "t.clean.b"
    abstract = False

    def process(self, ctx):
        ctx.context.truncation_log.append("B")
        return ctx


class AbortOnDecide(Plugin):
    name = "t.abort"
    abstract = False

    def process(self, ctx):
        ctx.context.truncation_log.append("ABORT")
        ctx.aborted = True
        ctx.abort_reason = "test"
        return ctx


class SkipMe(Plugin):
    name = "t.skip"
    abstract = False

    def process(self, ctx):
        ctx.context.truncation_log.append("SKIPME")
        return ctx


class AlwaysRun(Plugin):
    name = "t.always"
    abstract = False

    def process(self, ctx):
        ctx.context.truncation_log.append("ALWAYS")
        return ctx


class Fails(Plugin):
    name = "t.chain.fail"
    abstract = False

    def process(self, ctx):
        raise RuntimeError("boom")


class Succeeds(Plugin):
    name = "t.chain.ok"
    abstract = False

    def process(self, ctx):
        ctx.context.truncation_log.append("OK")
        return ctx


def _recipe():
    return {
        "name": "test-recipe",
        "stages": {
            "clean": {
                "mode": "list",
                "plugins": [{"name": StageA.name}, {"name": StageB.name}],
            },
            "decide": {
                "mode": "list",
                "plugins": [{"name": AbortOnDecide.name}],
            },
            "confidence": {
                "mode": "list",
                "plugins": [{"name": SkipMe.name}],
            },
            "validate": {
                "mode": "list",
                "plugins": [{"name": AlwaysRun.name}],
            },
        },
    }


def _registry():
    registry = Registry()
    for cls in (StageA, StageB, AbortOnDecide, SkipMe, AlwaysRun, Fails, Succeeds):
        registry.register(cls)
    return registry


def test_stages_run_in_order():
    pipeline = Pipeline(_registry(), _recipe())
    pipeline.setup()
    ctx = pipeline.process_item(Item(row_id="1"))
    assert ctx.context.truncation_log == ["A", "B", "ABORT", "ALWAYS"]


def test_abort_skips_later_stages_but_keeps_validate_and_output():
    pipeline = Pipeline(_registry(), _recipe())
    pipeline.setup()
    ctx = pipeline.process_item(Item(row_id="1"))
    assert ctx.aborted is True
    assert "SKIPME" not in ctx.context.truncation_log
    assert "ALWAYS" in ctx.context.truncation_log
    assert ctx.output_row is not None


def test_chain_falls_back_on_plugin_failure():
    recipe = {
        "name": "chain-recipe",
        "stages": {
            "decide": {
                "mode": "chain",
                "plugins": [{"name": Fails.name}, {"name": Succeeds.name}],
            }
        },
    }
    pipeline = Pipeline(_registry(), recipe)
    pipeline.setup()
    ctx = pipeline.process_item(Item(row_id="1"))
    assert ctx.context.truncation_log == ["OK"]


def test_trace_contains_events():
    pipeline = Pipeline(_registry(), _recipe())
    pipeline.setup()
    ctx = pipeline.process_item(Item(row_id="1"))
    stages = [event.stage for event in ctx.trace]
    assert "clean" in stages
    assert "decide" in stages
    assert "validate" in stages