#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


BENCHMARK_CODE = r"""
import array
import json
import math
import statistics
import time

import opuslib_next

FS = 48000
CHANNELS = 2
FRAME_SIZE = 960


def make_pcm16():
    pcm = array.array("h")
    for i in range(FRAME_SIZE):
        value = int(12000 * math.sin(2 * math.pi * 440 * i / FS))
        for _ in range(CHANNELS):
            pcm.append(value)
    return pcm.tobytes()


def make_pcm_float():
    pcm = array.array("f")
    for i in range(FRAME_SIZE):
        value = 0.3 * math.sin(2 * math.pi * 440 * i / FS)
        for _ in range(CHANNELS):
            pcm.append(value)
    return pcm.tobytes()


def measure(name, iterations, fn):
    samples = []
    for _ in range(5):
        start = time.perf_counter()
        for _ in range(iterations):
            fn()
        samples.append(time.perf_counter() - start)

    best = min(samples)
    avg = statistics.mean(samples)
    return {
        "name": name,
        "iterations": iterations,
        "best_seconds": best,
        "avg_seconds": avg,
        "best_us_per_op": best / iterations * 1_000_000,
        "avg_us_per_op": avg / iterations * 1_000_000,
    }


pcm16 = make_pcm16()
pcm_float = make_pcm_float()

encoder = opuslib_next.Encoder(FS, CHANNELS, opuslib_next.APPLICATION_AUDIO)
decoder = opuslib_next.Decoder(FS, CHANNELS)
packet = encoder.encode(pcm16, FRAME_SIZE)
float_packet = encoder.encode_float(pcm_float, FRAME_SIZE)


def create_destroy_encoder():
    instance = opuslib_next.Encoder(FS, CHANNELS, opuslib_next.APPLICATION_AUDIO)
    del instance


def create_destroy_decoder():
    instance = opuslib_next.Decoder(FS, CHANNELS)
    del instance

results = [
    measure("encoder_create_destroy", 500, create_destroy_encoder),
    measure("decoder_create_destroy", 500, create_destroy_decoder),
    measure("encode_pcm16", 2000, lambda: encoder.encode(pcm16, FRAME_SIZE)),
    measure("encode_float", 2000, lambda: encoder.encode_float(pcm_float, FRAME_SIZE)),
    measure("decode_pcm16", 2000, lambda: decoder.decode(packet, FRAME_SIZE)),
    measure("decode_float", 2000, lambda: decoder.decode_float(float_packet, FRAME_SIZE)),
]

print(json.dumps({
    "package_version": getattr(opuslib_next, "__version__", "unknown"),
    "results": results,
}))
"""


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )


def build_project(project_dir: Path, dist_dir: Path) -> Path:
    run(["uv", "build", "--out-dir", str(dist_dir)], cwd=project_dir)
    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        raise RuntimeError(f"No wheel built in {dist_dir}")
    return wheels[-1]


def make_venv(venv_dir: Path) -> Path:
    run(["uv", "venv", "--python", sys.executable, str(venv_dir)])
    python_name = "python.exe" if sys.platform.startswith("win") else "python"
    python_path = venv_dir / ("Scripts" if sys.platform.startswith("win") else "bin") / python_name
    return python_path


def install_wheel(python_path: Path, wheel_path: Path) -> None:
    run(["uv", "pip", "install", "--python", str(python_path), str(wheel_path)])


def install_requirement(
    python_path: Path,
    requirement: str,
    index_url: str | None = None,
) -> None:
    cmd = ["uv", "pip", "install", "--python", str(python_path)]
    if index_url:
        cmd.extend(["--index-url", index_url])
    cmd.append(requirement)
    run(cmd)


def run_benchmark(python_path: Path) -> dict:
    completed = run([str(python_path), "-c", BENCHMARK_CODE])
    return json.loads(completed.stdout)


def compare_metric(baseline_metric: dict, candidate_metric: dict) -> dict:
    baseline = baseline_metric["best_us_per_op"]
    candidate = candidate_metric["best_us_per_op"]
    delta = candidate - baseline
    change_pct = (delta / baseline) * 100 if baseline else 0.0
    return {
        "baseline_us_per_op": baseline,
        "candidate_us_per_op": candidate,
        "delta_us_per_op": delta,
        "change_pct": change_pct,
    }


def format_table(baseline_results: dict[str, dict], candidate_results: dict[str, dict]) -> str:
    lines = []
    header = f"{'benchmark':24} {'baseline(us)':>14} {'current(us)':>14} {'delta%':>10}"
    lines.append(header)
    lines.append("-" * len(header))
    for name in baseline_results:
        comparison = compare_metric(baseline_results[name], candidate_results[name])
        lines.append(
            f"{name:24} "
            f"{comparison['baseline_us_per_op']:14.2f} "
            f"{comparison['candidate_us_per_op']:14.2f} "
            f"{comparison['change_pct']:10.2f}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare benchmark results between a published release and the current worktree."
    )
    parser.add_argument(
        "--baseline-version",
        required=True,
        help="Published package version to install as the baseline, for example: 1.1.5",
    )
    parser.add_argument(
        "--baseline-index-url",
        help="Package index URL used with --baseline-version, for example TestPyPI.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to save the raw comparison JSON.",
    )
    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory(prefix="opuslib-bench-") as tmp:
        tmp_dir = Path(tmp)
        candidate_dist = tmp_dir / "candidate-dist"
        candidate_dist.mkdir()
        candidate_wheel = build_project(repo_dir, candidate_dist)

        baseline_python = make_venv(tmp_dir / "baseline-venv")
        candidate_python = make_venv(tmp_dir / "candidate-venv")

        install_requirement(
            baseline_python,
            f"opuslib-next=={args.baseline_version}",
            index_url=args.baseline_index_url,
        )
        baseline_label = f"published version {args.baseline_version}"

        install_wheel(candidate_python, candidate_wheel)

        baseline = run_benchmark(baseline_python)
        candidate = run_benchmark(candidate_python)

    baseline_results = {item["name"]: item for item in baseline["results"]}
    candidate_results = {item["name"]: item for item in candidate["results"]}

    print(f"Baseline: {baseline_label}")
    print(format_table(baseline_results, candidate_results))

    if args.output_json:
        payload = {
            "baseline_source": baseline_label,
            "baseline_result": baseline,
            "candidate": candidate,
        }
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote raw results to {args.output_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
