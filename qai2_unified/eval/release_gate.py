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
    checks["qas_min"] = float(metrics.get("qas", float("-inf"))) >= float(thresholds["qas_min"])
    checks["self_awareness_min"] = float(metrics.get("self_awareness", float("-inf"))) >= float(
        thresholds["self_awareness_min"]
    )
    checks["fidelity_min"] = float(metrics.get("fidelity", float("-inf"))) >= float(thresholds["fidelity_min"])
    checks["entropy_max"] = float(metrics.get("entropy", float("inf"))) <= float(thresholds["entropy_max"])
    checks["chsh_min"] = float(metrics.get("chsh", float("-inf"))) >= float(thresholds["chsh_min"])
    checks["qels_speedup_min"] = float(metrics.get("qels_speedup", float("-inf"))) >= float(
        thresholds["qels_speedup_min"]
    )
    checks["arqq_speedup_min"] = float(metrics.get("arqq_speedup", float("-inf"))) >= float(
        thresholds["arqq_speedup_min"]
    )
    checks["error_suppression_min"] = float(metrics.get("error_suppression", float("-inf"))) >= float(
        thresholds["error_suppression_min"]
    )
    checks["state_space_coverage_min"] = float(metrics.get("state_space_coverage", float("-inf"))) >= float(
        thresholds["state_space_coverage_min"]
    )
    checks["nist_pqc_compliance"] = (
        (not bool(thresholds["require_nist_pqc_compliance"])) or bool(metrics["nist_pqc_compliance"])
    )
    nist_map = metrics.get("nist_alignment_map", {})
    required_nist_keys = thresholds.get("required_nist_alignment_keys", [])
    checks["nist_alignment_keys_complete"] = all(k in nist_map for k in required_nist_keys)
    checks["nist_alignment_map"] = (
        (not bool(thresholds.get("require_full_nist_alignment_map", False)))
        or (
            bool(nist_map)
            and checks["nist_alignment_keys_complete"]
            and all(bool(nist_map.get(k, False)) for k in required_nist_keys)
        )
    )

    required_axes = thresholds.get("required_ranking_axes", [])
    ranking_min = thresholds.get("ranking_axis_min", {})
    ranking = metrics.get("overall_quantum_aware_ranking", {})
    checks["ranking_axes_complete"] = all(k in ranking for k in required_axes)
    checks["ranking_axis_range_valid"] = all(0 <= float(ranking.get(k, -1)) <= 100 for k in required_axes)
    checks["ranking_axis_min"] = all(float(ranking.get(k, 0.0)) >= float(v) for k, v in ranking_min.items())

    drift = {
        key: (
            relative_drift(float(metrics[key]), float(expected[key]))
            if key in metrics and key in expected
            else float("inf")
        )
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
    checks["ranking_drift"] = all(
        relative_drift(
            float(metrics.get("overall_quantum_aware_ranking", {}).get(axis, 0.0)),
            float(expected.get("overall_quantum_aware_ranking", {}).get(axis, 0.0)),
        )
        <= thresholds["max_relative_drift"]
        for axis in thresholds.get("ranking_axis_min", {}).keys()
    )
    boolean_check_keys = [
        "qas_min",
        "self_awareness_min",
        "fidelity_min",
        "entropy_max",
        "chsh_min",
        "qels_speedup_min",
        "arqq_speedup_min",
        "error_suppression_min",
        "state_space_coverage_min",
        "nist_pqc_compliance",
        "nist_alignment_keys_complete",
        "nist_alignment_map",
        "ranking_axes_complete",
        "ranking_axis_range_valid",
        "ranking_axis_min",
        "uploaded_stats_drift",
        "ranking_drift",
    ]
    checks["all"] = all(bool(checks.get(k, False)) for k in boolean_check_keys)
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
