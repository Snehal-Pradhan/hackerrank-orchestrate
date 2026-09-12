from __future__ import annotations

import os
from typing import Any, Dict

import yaml

from .pipeline import STAGES


class Recipe:
    @staticmethod
    def load(path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"recipe not found: {path}")
        with open(path, "r", encoding="utf-8") as fh:
            recipe = yaml.safe_load(fh) or {}
        Recipe.validate(recipe)
        return recipe

    @staticmethod
    def validate(recipe: Dict[str, Any]) -> None:
        if not isinstance(recipe.get("name"), str):
            raise ValueError("recipe must have a string 'name'")
        stages = recipe.get("stages")
        if not isinstance(stages, dict):
            raise ValueError("recipe must have a 'stages' mapping")
        allowed = set(STAGES)
        unknown = set(stages) - allowed
        if unknown:
            raise ValueError(f"unknown stages {sorted(unknown)}; allowed: {STAGES}")
        for stage_name, spec in stages.items():
            if not isinstance(spec, dict):
                raise ValueError(f"stage {stage_name!r} spec must be a mapping")
            plugins = spec.get("plugins", [])
            if not isinstance(plugins, list):
                raise ValueError(f"stage {stage_name!r} 'plugins' must be a list")
            for entry in plugins:
                if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
                    raise ValueError(f"stage {stage_name!r} has a malformed plugin entry")