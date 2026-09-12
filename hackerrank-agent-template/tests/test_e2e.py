from __future__ import annotations

import csv
from pathlib import Path

from core.runner import run_pipeline
from plugins.observability.json_log import JsonLog

ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "1": "RESPOND",
    "2": "ESCALATE",
    "3": "BLOCK",
    "4": "ESCALATE",
    "5": "RESPOND",
    "6": "ESCALATE",
    "7": "RESPOND",
}


def _decisions(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["row_id"]: row["decision"] for row in csv.DictReader(fh)}


def test_end_to_end(monkeypatch, tmp_path):
    monkeypatch.chdir(ROOT)
    output = tmp_path / "out.csv"
    trace = tmp_path / "trace.jsonl"

    stats = run_pipeline(
        recipe_path=str(ROOT / "recipes/text-classification.yaml"),
        input_path=str(ROOT / "examples/sample_tickets.csv"),
        output_path=str(output),
        trace_path=str(trace),
    )

    assert stats["items"] == 7
    assert stats["rows"] == 7
    assert stats["quarantined"] == 0
    assert _decisions(output) == EXPECTED
    assert trace.exists()
    assert trace.read_text(encoding="utf-8").strip()


def test_determinism(monkeypatch, tmp_path):
    monkeypatch.chdir(ROOT)
    first = tmp_path / "a.csv"
    second = tmp_path / "b.csv"
    run_pipeline(
        recipe_path=str(ROOT / "recipes/text-classification.yaml"),
        input_path=str(ROOT / "examples/sample_tickets.csv"),
        output_path=str(first),
    )
    run_pipeline(
        recipe_path=str(ROOT / "recipes/text-classification.yaml"),
        input_path=str(ROOT / "examples/sample_tickets.csv"),
        output_path=str(second),
    )
    assert first.read_bytes() == second.read_bytes()


def test_evaluate_matches_gold(monkeypatch, tmp_path):
    monkeypatch.chdir(ROOT)
    output = tmp_path / "out.csv"
    run_pipeline(
        recipe_path=str(ROOT / "recipes/text-classification.yaml"),
        input_path=str(ROOT / "examples/sample_tickets.csv"),
        output_path=str(output),
    )
    assert _decisions(output) == EXPECTED


def test_json_log_flush(tmp_path):
    log_path = tmp_path / "log.jsonl"
    sink = JsonLog({"path": str(log_path)})
    sink.setup()
    from core.contracts import ExecutionContext

    sink.process(ExecutionContext(item=None))
    sink.flush()
    assert log_path.exists()
    assert log_path.read_text(encoding="utf-8").strip()