from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import Any, Dict, List, Optional, Type

from .plugin import Plugin


class Registry:
    def __init__(self) -> None:
        self._classes: List[Type[Plugin]] = []
        self._by_name: Dict[str, Type[Plugin]] = {}

    def register(self, cls: Type[Plugin]) -> None:
        if not (inspect.isclass(cls) and issubclass(cls, Plugin)):
            raise TypeError(f"{cls} is not a Plugin subclass")
        if getattr(cls, "abstract", False):
            return
        if cls.name in self._by_name and self._by_name[cls.name] is cls:
            return
        if cls.name in self._by_name:
            raise ValueError(f"duplicate plugin name {cls.name}")
        self._classes.append(cls)
        self._by_name[cls.name] = cls

    def discover(self, package, recursive: bool = True) -> "Registry":
        for mod_info in pkgutil.iter_modules(package.__path__):
            module = importlib.import_module(f"{package.__name__}.{mod_info.name}")
            if recursive and hasattr(module, "__path__"):
                self.discover(module)
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if cls is Plugin:
                    continue
                if issubclass(cls, Plugin) and getattr(cls, "name", None):
                    self.register(cls)
        return self

    def get(self, name: str) -> Type[Plugin]:
        try:
            return self._by_name[name]
        except KeyError:
            available = sorted(self._by_name)
            raise KeyError(f"unknown plugin {name!r}; available: {available}")

    def instantiate(self, name: str, config: Optional[Dict[str, Any]] = None) -> Plugin:
        instance = self.get(name)(config)
        instance.bind(self)
        return instance

    def by_capability(self, capability: str) -> List[Type[Plugin]]:
        return [cls for cls in self._classes if capability in getattr(cls, "provides", [])]

    def names(self) -> List[str]:
        return sorted(self._by_name)