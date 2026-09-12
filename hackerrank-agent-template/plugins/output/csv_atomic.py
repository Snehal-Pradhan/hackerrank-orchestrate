from __future__ import annotations

import csv
import os
from typing import List

from core.contracts import OutputRow
from core.plugin import Plugin


class AtomicCsvWriter(Plugin):
    category = "output"
    name = "output.csv"
    version = "0.1.0"
    abstract = False
    actor = True
    provides = ["output.csv"]
    requires = []
    config_schema = {"columns": "list", "encoding": str}

    def write(self, rows: List[OutputRow], path: str) -> None:
        columns = self.config.get("columns", ["row_id", "decision"])
        encoding = self.config.get("encoding", "utf-8")
        tmp = f"{path}.tmp"
        with open(tmp, "w", newline="", encoding=encoding) as fh:
            writer = csv.DictWriter(fh, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                record = {"row_id": row.row_id, **row.columns}
                writer.writerow({column: record.get(column, "") for column in columns})
        os.replace(tmp, path)