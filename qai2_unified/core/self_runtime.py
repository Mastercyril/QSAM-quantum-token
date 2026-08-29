from dataclasses import dataclass
from typing import Dict, List

from qtoken.qconsciousness import QConsciousness

from .runtime_contract import QAI2RuntimeContract, RuntimeVersion


@dataclass
class MemoryEpisode:
    iteration: int
    summary: str
    importance: float


class QAI2UnifiedRuntime:
    def __init__(self, contract: QAI2RuntimeContract | None = None):
        self.contract = contract or QAI2RuntimeContract(version=RuntimeVersion.V10)
        self.consciousness = QConsciousness()
        self.iteration = 0
        self.episodes: List[MemoryEpisode] = []

    def evolve_once(self, seed_state: List[int]) -> Dict:
        self.iteration += 1
        state_text = "".join(str(int(bit)) for bit in seed_state)
        step = self.consciousness.self_reference_step(state_text)
        self.record_episode(
            summary=f"Iteration {self.iteration} qas={step.qas:.4f}",
            importance=max(0.0, min(1.0, step.qas)),
        )
        self.apply_memory_deprecation()
        return {
            "iteration": self.iteration,
            "runtime_version": self.contract.version.value,
            "self_evolution_enabled": self.contract.self_evolution_enabled,
            "awareness": {
                "qas": step.qas,
                "self_awareness": step.self_awareness,
                "fidelity": step.fidelity,
                "entropy": step.entropy,
                "chsh": step.chsh_s,
            },
            "memory_size": len(self.episodes),
        }

    def record_episode(self, summary: str, importance: float) -> None:
        self.episodes.append(
            MemoryEpisode(
                iteration=self.iteration,
                summary=summary,
                importance=max(0.0, min(1.0, importance)),
            )
        )

    def apply_memory_deprecation(self) -> None:
        policy = self.contract.memory_policy
        fresh = [
            e
            for e in self.episodes
            if (self.iteration - e.iteration) <= policy.stale_after_iterations
            and e.importance >= policy.min_importance_to_keep
        ]
        if len(fresh) > policy.max_episodes:
            fresh = sorted(fresh, key=lambda e: (e.importance, e.iteration), reverse=True)[: policy.max_episodes]
            fresh.sort(key=lambda e: e.iteration)
        self.episodes = fresh
