from __future__ import annotations

from typing import Optional

from core.contracts import Decision, ExecutionContext
from core.plugin import Plugin


class LevelPlugin(Plugin):
    category = "policy"
    abstract = True

    def decide(self, ctx: ExecutionContext) -> Optional[Decision]:
        return None