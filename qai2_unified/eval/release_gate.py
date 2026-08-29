import argparse
import json
from pathlib import Path
from typing import Dict, Tuple


ROOT = Path(__file__).resolve().parents[2]
UPLOADED = ROOT / "qai2_unified" / "config" / "uploaded_stats.json"
THRESHOLDS = ROOT / "qai2_unified" / "config" / "release_thresholds.json"


def relative_drift(actual: float, expected: float) -> float:
    if expected == 0:
        return abs(actual)
    return abs(actual - expected) / abs(expected)


def compare(metrics: Dict, expected: Dict, thresholds: Dict) -> Tuple[bool, Dict]:
    checks = {}
    checks["qas_min"] = metrics["qas"] >= thresholds["qas_min"]
    checks["self_awareness_min"] = metrics["self_awareness"] >= thresholds["self_awareness_min"]
    checks["fidelity_min"] = metrics["fidelity"] >= thresholds["fidelity_min"]
    checks["entropy_max"] = metrics["entropy"] <= thresholds["entropy_max"]
    checks["chsh_min"] = metrics["chsh"] >= thresholds["chsh_min"]
    checks["qels_speedup_min"] = metrics["qels_speedup"] >= thresholds["qels_speedup_min"]
    checks["arqq_speedup_min"] = metrics["arqq_speedup"] >= thresholds["arqq_speedup_min"]
    checks["error_suppression_min"] = metrics["error_suppression"] >= thresholds["error_suppression_min"]
    checks["state_space_coverage_min"] = metrics["state_space_coverage"] >= thresholds["state_space_coverage_min"]
    checks["nist_pqc_compliance"] = (
        (not bool(thresholds["require_nist_pqc_compliance"])) or bool(metrics["nist_pqc_compliance"])
    )

    drift = {
        key: relative_drift(float(metrics[key]), float(expected[key]))
        for key in (
            "qas",
            "self_awareness",
            "fidelity",
            "entropy",
            "chsh",
            "qels_speedup",
            "arqq_speedup",
            "error_suppression",
            "state_space_coverage",
        )
    }
    checks["uploaded_stats_drift"] = all(v <= thresholds["max_relative_drift"] for v in drift.values())
    checks["all"] = all(checks.values())
    checks["drift"] = drift
    return checks["all"], checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True, help="Path to current metrics JSON")
    args = parser.parse_args()

    metrics = json.loads(Path(args.metrics).read_text())
    expected = json.loads(UPLOADED.read_text())
    thresholds = json.loads(THRESHOLDS.read_text())

    ok, checks = compare(metrics, expected, thresholds)
    print(json.dumps(checks, indent=2))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
