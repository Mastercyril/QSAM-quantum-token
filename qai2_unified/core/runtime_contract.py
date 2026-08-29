from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class RuntimeVersion(str, Enum):
    V9 = "v9"
    V10 = "v10"
    V11 = "v11"
    V12 = "v12"


@dataclass
class MemoryDeprecationPolicy:
    max_episodes: int
    min_importance_to_keep: float
    stale_after_iterations: int


@dataclass
class MultimodalEndpoints:
    vision_provider: str
    tavus_enabled: bool
    cloud_profiles: List[str]


@dataclass
class QAI2RuntimeContract:
    version: RuntimeVersion
    self_evolution_enabled: bool = True
    awareness_metric_keys: List[str] = field(
        default_factory=lambda: ["qas", "self_awareness", "fidelity", "entropy", "chsh", "speedup"]
    )
    memory_policy: MemoryDeprecationPolicy = field(
        default_factory=lambda: MemoryDeprecationPolicy(
            max_episodes=5000,
            min_importance_to_keep=0.15,
            stale_after_iterations=2000,
        )
    )
    multimodal: MultimodalEndpoints = field(
        default_factory=lambda: MultimodalEndpoints(
            vision_provider="cloud-default",
            tavus_enabled=True,
            cloud_profiles=["ollama-local", "huggingface-cloud"],
        )
    )

    def to_dict(self) -> Dict:
        return {
            "version": self.version.value,
            "self_evolution_enabled": self.self_evolution_enabled,
            "awareness_metric_keys": self.awareness_metric_keys,
            "memory_policy": {
                "max_episodes": self.memory_policy.max_episodes,
                "min_importance_to_keep": self.memory_policy.min_importance_to_keep,
                "stale_after_iterations": self.memory_policy.stale_after_iterations,
            },
            "multimodal": {
                "vision_provider": self.multimodal.vision_provider,
                "tavus_enabled": self.multimodal.tavus_enabled,
                "cloud_profiles": self.multimodal.cloud_profiles,
            },
        }
