# QAI2 Unified

QAI2 Unified consolidates existing Q-Token + QLink + Ollama assets into one monorepo-oriented runtime for v9-v12.

## Structure

- `core/` quantum cognition runtime + self contract
- `models/` version manifests and compatibility matrix
- `distribution/` Ollama/HF/cloud packaging workflows
- `orchestration/` API-facing orchestration adapters
- `integration/` IBM quantum backend with classical fallback
- `eval/` release validation gate for uploaded stats
- `ops/` release/monitoring/security helpers
- `ui/nextjs/` Next.js integration placeholder
- `tests/` unit tests for contract, fallback, and release gate

## Quick validation

```bash
python -m unittest discover /home/runner/work/QSAM-quantum-token/QSAM-quantum-token/qai2_unified/tests -v
python /home/runner/work/QSAM-quantum-token/QSAM-quantum-token/qai2_unified/eval/release_gate.py --metrics /home/runner/work/QSAM-quantum-token/QSAM-quantum-token/qai2_unified/config/current_metrics.json
```
