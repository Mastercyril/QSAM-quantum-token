import json
import unittest
from copy import deepcopy
from pathlib import Path

from qai2_unified.eval.release_gate import compare


class ReleaseGateTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[2]
        self.metrics = json.loads((root / "qai2_unified/config/current_metrics.json").read_text())
        self.expected = json.loads((root / "qai2_unified/config/uploaded_stats.json").read_text())
        self.thresholds = json.loads((root / "qai2_unified/config/release_thresholds.json").read_text())

    def test_compare_passes_with_current_metrics(self):
        ok, checks = compare(self.metrics, self.expected, self.thresholds)
        self.assertTrue(ok)
        self.assertTrue(checks["all"])

    def test_compare_fails_when_required_nist_key_missing(self):
        bad_metrics = deepcopy(self.metrics)
        bad_metrics["nist_alignment_map"].pop("govern_quantum_state_verification", None)
        ok, checks = compare(bad_metrics, self.expected, self.thresholds)
        self.assertFalse(ok)
        self.assertFalse(checks["nist_alignment_keys_complete"])

    def test_compare_fails_when_ranking_axis_out_of_range(self):
        bad_metrics = deepcopy(self.metrics)
        bad_metrics["overall_quantum_aware_ranking"]["reasoning"] = 120
        ok, checks = compare(bad_metrics, self.expected, self.thresholds)
        self.assertFalse(ok)
        self.assertFalse(checks["ranking_axis_range_valid"])

    def test_compare_fails_gracefully_when_core_metric_missing(self):
        bad_metrics = deepcopy(self.metrics)
        bad_metrics.pop("chsh", None)
        ok, checks = compare(bad_metrics, self.expected, self.thresholds)
        self.assertFalse(ok)
        self.assertFalse(checks["chsh_min"])


if __name__ == "__main__":
    unittest.main()
