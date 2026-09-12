from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .contracts import ExecutionContext


class Plugin(ABC):
    category: str = "generic"
    name: str = "base"
    version: str = "0.1.0"
    abstract: bool = True
    provides: List[str] = []
    requires: List[str] = []
    config_schema: Dict[str, Any] = {}
    actor: bool = False

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.registry = None
        self.validate_config()

    def validate_config(self) -> None:
        unknown = set(self.config) - set(self.config_schema)
        if unknown:
            raise ValueError(f"{self.name}: unknown config keys {sorted(unknown)}")

    def bind(self, registry) -> None:
        self.registry = registry

    def setup(self) -> None:
        pass

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        return ctx

    def can_handle(self, ctx: ExecutionContext) -> bool:
        return True

    def shutdown(self) -> None:
        pass

    def health(self) -> Dict[str, Any]:
        return {"plugin": self.name, "ok": True}