import time
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class IBMRunMetadata:
    backend: str
    used_quantum: bool
    fallback_reason: str
    started_at_epoch: float
    ended_at_epoch: float
    operation: str

    def to_dict(self) -> Dict:
        return {
            "backend": self.backend,
            "used_quantum": self.used_quantum,
            "fallback_reason": self.fallback_reason,
            "started_at_epoch": self.started_at_epoch,
            "ended_at_epoch": self.ended_at_epoch,
            "operation": self.operation,
        }


class QuantumReasoningBackend:
    def __init__(self, preferred_backend: str = "ibm_torino"):
        self.preferred_backend = preferred_backend

    def _try_quantum(self, numbers: List[float]) -> float:
        try:
            from qiskit import QuantumCircuit  # type: ignore

            _ = QuantumCircuit(1)
            return float(sum(numbers))
        except Exception as exc:
            raise RuntimeError(str(exc)) from exc

    def _classical_fallback(self, numbers: List[float]) -> float:
        return float(sum(numbers))

    def run_reasoning_math(self, numbers: List[float]) -> Dict:
        started = time.time()
        used_quantum = True
        fallback_reason = ""
        try:
            result = self._try_quantum(numbers)
        except Exception as exc:
            used_quantum = False
            fallback_reason = f"quantum_unavailable:{exc}"
            result = self._classical_fallback(numbers)

        ended = time.time()
        metadata = IBMRunMetadata(
            backend=self.preferred_backend if used_quantum else "classical-fallback",
            used_quantum=used_quantum,
            fallback_reason=fallback_reason,
            started_at_epoch=started,
            ended_at_epoch=ended,
            operation="reasoning_math_sum",
        )
        return {"result": result, "run_metadata": metadata.to_dict()}
