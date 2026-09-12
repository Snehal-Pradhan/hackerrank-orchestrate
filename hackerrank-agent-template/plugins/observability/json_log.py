from __future__ import annotations

import json
from typing import List

from core.contracts import ExecutionContext
from core.plugin import Plugin


class JsonLog(Plugin):
    category = "observability"
    name = "obs.json_log"
    version = "0.1.0"
    abstract = False
    actor = True
    provides = ["obs.json_log"]
    requires = []
    config_schema = {"path": str}

    def __init__(self, config=None) -> None:
        super().__init__(config)
        self._lines: List[str] = []

    def setup(self) -> None:
        self._lines = []

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        self._lines.append(json.dumps(ctx.model_dump()))
        return ctx

    def flush(self) -> None:
        path = self.config.get("path")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self._lines) + "\n")