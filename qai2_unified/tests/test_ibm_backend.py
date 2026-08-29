import unittest

from qai2_unified.integration.ibm_backend import QuantumReasoningBackend


class IBMBackendTest(unittest.TestCase):
    def test_fallback_runs(self):
        backend = QuantumReasoningBackend()
        out = backend.run_reasoning_math([1, 2, 3])
        self.assertEqual(out["result"], 6.0)
        self.assertIn("used_quantum", out["run_metadata"])
        self.assertIn("fallback_reason", out["run_metadata"])


if __name__ == "__main__":
    unittest.main()
