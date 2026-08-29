from typing import Dict, List

from qai2_unified.core.self_runtime import QAI2UnifiedRuntime


class UnifiedOrchestrator:
    def __init__(self, runtime: QAI2UnifiedRuntime | None = None):
        self.runtime = runtime or QAI2UnifiedRuntime()

    def run_cycle(self, seed_state: List[int]) -> Dict:
        return self.runtime.evolve_once(seed_state)
