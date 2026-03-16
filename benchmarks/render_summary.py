#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

REGRESSION_THRESHOLD_PCT = 8.0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render benchmark comparison JSON as Markdown."
    )
    parser.add_argument("result_json", type=Path)
    parser.add_argument("--python-version", required=True)
    args = parser.parse_args()

    payload = json.loads(args.result_json.read_text(encoding="utf-8"))
    baseline = {
        item["name"]: item for item in payload["baseline_result"]["results"]
    }
    candidate = {
        item["name"]: item for item in payload["candidate"]["results"]
    }

    print(f"### Python {args.python_version}")
    print()
    print(f"Baseline: `{payload['baseline_source']}`")
    print()
    print("| Benchmark | Baseline median (us/op) | Current median (us/op) | Delta % | Status |")
    print("| --- | ---: | ---: | ---: | --- |")

    regressions = []

    for name in baseline:
        baseline_us = baseline[name]["median_us_per_op"]
        candidate_us = candidate[name]["median_us_per_op"]
        change_pct = ((candidate_us - baseline_us) / baseline_us) * 100 if baseline_us else 0.0
        status = "ok"
        if change_pct >= REGRESSION_THRESHOLD_PCT:
            status = "regression"
            regressions.append((name, change_pct))
        print(
            f"| `{name}` | {baseline_us:.2f} | {candidate_us:.2f} | {change_pct:.2f}% | {status} |"
        )

    print()
    if regressions:
        print(f"Regressions over threshold ({REGRESSION_THRESHOLD_PCT:.1f}%):")
        print()
        for name, change_pct in regressions:
            print(f"- `{name}`: {change_pct:.2f}%")
    else:
        print(f"No regressions over {REGRESSION_THRESHOLD_PCT:.1f}%.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
