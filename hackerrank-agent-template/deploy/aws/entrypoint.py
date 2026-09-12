"""Container entrypoint for AWS Fargate/S3-batch execution of the agent pipeline."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

from core.runner import run_pipeline


def _s3_key(bucket: str, key: str) -> None:
    import boto3

    return None


def _download(bucket: str, key: str, dest: str) -> None:
    import boto3

    client = boto3.client("s3")
    client.download_file(bucket, key, dest)


def _upload(bucket: str, key: str, src: str) -> None:
    import boto3

    client = boto3.client("s3")
    client.upload_file(src, bucket, key)


def _parse_uri(uri: str) -> tuple[str, str]:
    if uri.startswith("s3://"):
        parts = uri[len("s3://"):].split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        return bucket, key
    return "", uri


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run agent pipeline from S3 and write output back to S3.")
    parser.add_argument("--recipe", required=True, help="path to recipe YAML inside container")
    parser.add_argument("--input", required=True, help="s3://bucket/key to input CSV")
    parser.add_argument("--output", required=True, help="s3://bucket/key destination for output CSV")
    parser.add_argument("--trace", required=False, default="", help="s3://bucket/key destination for JSONL trace")
    parser.add_argument("--temp-dir", required=False, default="", help="scratch dir (default: tempfile)")
    args = parser.parse_args(argv)

    in_bucket, in_key = _parse_uri(args.input)
    out_bucket, out_key = _parse_uri(args.output)
    trace_bucket, trace_key = _parse_uri(args.trace) if args.trace else ("", "")

    if not in_bucket or not in_key:
        print(f"bad --input URI: {args.input!r}", file=sys.stderr)
        return 2

    scratch = Path(args.temp_dir or tempfile.mkdtemp(prefix="agent-batch-"))
    scratch.mkdir(parents=True, exist_ok=True)
    local_input = scratch / "input.csv"
    local_output = scratch / "output.csv"
    local_trace = str(scratch / "trace.jsonl")

    _download(in_bucket, in_key, str(local_input))
    print(f"downloaded s3://{in_bucket}/{in_key} -> {local_input}")

    stats = run_pipeline(
        recipe_path=args.recipe,
        input_path=str(local_input),
        output_path=str(local_output),
        trace_path=local_trace if trace_key else "",
    )
    print(json.dumps(stats, indent=2))

    _upload(out_bucket, out_key, str(local_output))
    print(f"uploaded {local_output} -> s3://{out_bucket}/{out_key}")
    if trace_key:
        _upload(trace_bucket, trace_key, local_trace)
        print(f"uploaded {local_trace} -> s3://{trace_bucket}/{trace_key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
