# QAI2 Unified

QAI2 Unified consolidates existing Q-Token + QLink + Ollama assets into one monorepo-oriented runtime for v9-v12.

## Structure

- `core/` quantum cognition runtime + self contract
- `models/` version manifests and compatibility matrix
- `distribution/` Ollama/HF/cloud packaging workflows
- `orchestration/` API-facing orchestration adapters; `server.py` exposes a stdlib HTTP server
- `integration/` IBM quantum backend with classical fallback
- `eval/` release validation gate for uploaded stats
- `ops/` release/monitoring/security helpers
- `ui/nextjs/` Next.js integration placeholder
- `tests/` unit tests for contract, fallback, release gate, and HTTP server

## Quick validation

```bash
python -m unittest discover qai2_unified/tests -v
python qai2_unified/eval/release_gate.py --metrics qai2_unified/config/current_metrics.json
```

## HTTP orchestration server

`orchestration/server.py` wraps `UnifiedOrchestrator` as a lightweight stdlib HTTP server so external clients (Next.js UI, Puter workers, CLI tools) can trigger evolution cycles without a direct Python import.

```bash
# Start on default port 8000:
python -m qai2_unified.orchestration.server

# Custom host/port:
python -m qai2_unified.orchestration.server --host 0.0.0.0 --port 9090
```

| Method | Path      | Body / Response |
|--------|-----------|-----------------|
| GET    | `/health` | `{"status":"ok","version":"vN"}` |
| POST   | `/cycle`  | body: `{"seed":[0,1,...]}` → `{"iteration":N,...}` |
