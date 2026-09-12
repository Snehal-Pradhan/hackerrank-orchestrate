from __future__ import annotations

from core.contracts import OutputRow
from plugins.output.csv_atomic import AtomicCsvWriter


def test_atomic_write(tmp_path):
    path = tmp_path / "out.csv"
    rows = [
        OutputRow(row_id="1", columns={"decision": "RESPOND"}),
        OutputRow(row_id="2", columns={"decision": "ESCALATE"}),
    ]
    AtomicCsvWriter({"columns": ["row_id", "decision"]}).write(rows, str(path))

    assert path.exists()
    assert not (tmp_path / "out.csv.tmp").exists()
    content = path.read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    assert lines[0] == "row_id,decision"
    assert "1,RESPOND" in lines[1]
    assert "2,ESCALATE" in lines[2]


def test_writer_overwrites_existing_file(tmp_path):
    path = tmp_path / "out.csv"
    path.write_text("stale", encoding="utf-8")
    rows = [OutputRow(row_id="9", columns={"decision": "BLOCK"})]
    AtomicCsvWriter({"columns": ["row_id", "decision"]}).write(rows, str(path))
    assert path.read_text(encoding="utf-8").strip() == "row_id,decision\n9,BLOCK"