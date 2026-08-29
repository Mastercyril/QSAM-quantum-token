import unittest

from qai2_unified.core.runtime_contract import QAI2RuntimeContract, RuntimeVersion


class RuntimeContractTest(unittest.TestCase):
    def test_contract_serializes(self):
        contract = QAI2RuntimeContract(version=RuntimeVersion.V12)
        data = contract.to_dict()
        self.assertEqual(data["version"], "v12")
        self.assertTrue(data["self_evolution_enabled"])
        self.assertIn("qas", data["awareness_metric_keys"])


if __name__ == "__main__":
    unittest.main()
