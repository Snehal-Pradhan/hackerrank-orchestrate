from __future__ import annotations

import argparse
import csv
import json

from .contracts import OutputRow
from .recipe import Recipe
from .runner import build_registry, evaluate, run_pipeline


def _load_rows(path: str) -> list[OutputRow]:
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for record in csv.DictReader(fh):
            rows.append(OutputRow(row_id=record["row_id"], columns={"decision": record["decision"]}))
    return rows


def _cmd_run(args) -> int:
    stats = run_pipeline(args.recipe, args.input, args.output, trace_path=args.trace or "")
    print(json.dumps(stats, indent=2))
    if args.gold:
        report = evaluate(args.gold, _load_rows(args.output))
        print(json.dumps(report, indent=2))
    return 0


def _cmd_plugins(args) -> int:
    registry = build_registry()
    for name in registry.names():
        cls = registry.get(name)
        print(f"{name:24s} {cls.category:14s} provides={cls.provides}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="agent", description="HackerRank agent template CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="run the pipeline over an input file")
    run_p.add_argument("--recipe", required=True)
    run_p.add_argument("--input", required=True)
    run_p.add_argument("--output", required=True)
    run_p.add_argument("--gold")
    run_p.add_argument("--trace")

    sub.add_parser("plugins", help="list registered plugins")

    args = parser.parse_args(argv)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "plugins":
        return _cmd_plugins(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())