import json
import tempfile
import unittest
from pathlib import Path

from qai2_unified.eval.release_gate import compare


class ReleaseGateTest(unittest.TestCase):
    def test_compare_passes_with_current_metrics(self):
        root = Path(__file__).resolve().parents[2]
        metrics = json.loads((root / "qai2_unified/config/current_metrics.json").read_text())
        expected = json.loads((root / "qai2_unified/config/uploaded_stats.json").read_text())
        thresholds = json.loads((root / "qai2_unified/config/release_thresholds.json").read_text())
        ok, checks = compare(metrics, expected, thresholds)
        self.assertTrue(ok)
        self.assertTrue(checks["all"])


if __name__ == "__main__":
    unittest.main()
