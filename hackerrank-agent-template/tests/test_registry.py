import pytest

from core.contracts import Item
from core.registry import Registry
from core.plugin import Plugin


class Dummy(Plugin):
    name = "t.dummy"
    version = "0.1.0"
    abstract = False

    def process(self, ctx):
        return ctx


def test_discover_registers_starter_plugins():
    import plugins

    registry = Registry().discover(plugins)
    names = set(registry.names())
    for expected in (
        "input.csv",
        "cleaning.normalize",
        "features.text",
        "features.risk",
        "perception.mock",
        "policy.cascade",
        "policy.safety",
        "policy.domain",
        "policy.fallback",
        "confidence.band",
        "validation.output_contract",
        "output.csv",
        "obs.json_log",
    ):
        assert expected in names, expected


def test_abstract_base_is_not_registered():
    import plugins

    registry = Registry().discover(plugins)
    assert "base" not in registry.names()


def test_duplicate_name_rejected():
    registry = Registry()
    registry.register(Dummy)

    class Duplicate(Dummy):
        name = "t.dummy"

    with pytest.raises(ValueError):
        registry.register(Duplicate)


def test_unknown_plugin_raises():
    registry = Registry()
    with pytest.raises(KeyError):
        registry.instantiate("does.not.exist")


def test_by_capability():
    import plugins

    registry = Registry().discover(plugins)
    vector = registry.by_capability("policy.safety")
    assert any(cls.name == "policy.safety" for cls in vector)


def test_config_validation_rejects_unknown_keys():
    with pytest.raises(ValueError):
        Dummy({"nope": 1})