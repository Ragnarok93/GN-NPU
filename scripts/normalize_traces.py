#!/usr/bin/env python3
"""Normalize a validated GN-NPU JSONL trace capture to Parquet."""

from __future__ import annotations

import argparse
import sys

from gn_npu.ingest.jsonl import TraceParseError, normalize_jsonl_to_parquet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input JSON Lines trace path")
    parser.add_argument("output", help="output Parquet path")
    args = parser.parse_args()

    try:
        count = normalize_jsonl_to_parquet(args.input, args.output)
    except (TraceParseError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"normalized {count} events: {args.input} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
