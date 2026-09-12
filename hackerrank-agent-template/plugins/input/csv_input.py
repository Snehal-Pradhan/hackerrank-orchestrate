from __future__ import annotations

import csv
from typing import Any, Dict, List

from core.contracts import Item
from core.plugin import Plugin


class CsvInput(Plugin):
    category = "input"
    name = "input.csv"
    version = "0.1.0"
    abstract = False
    provides = ["input.csv"]
    requires = []
    config_schema = {"row_id_field": str, "encoding": str, "has_header": bool}

    def load(self, path: str) -> List[Item]:
        encoding = self.config.get("encoding", "utf-8")
        row_id_field = self.config.get("row_id_field", "")
        items: List[Item] = []
        with open(path, newline="", encoding=encoding) as fh:
            reader = csv.DictReader(fh)
            for index, record in enumerate(reader, start=1):
                rid = record.get(row_id_field) if row_id_field else None
                if not rid:
                    rid = str(index)
                items.append(Item(row_id=str(rid), fields=dict(record)))
        return items