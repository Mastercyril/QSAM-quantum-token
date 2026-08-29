# Monitoring and Rollback

## Monitoring
- Capture every run metadata payload from `QuantumReasoningBackend.run_reasoning_math`.
- Alert if quantum fallback rate exceeds 20% over 1 hour.
- Alert if release-gate metrics drift above threshold.

## Rollback
1. Pin inference profile to previous stable manifest (`v11` if `v12` fails).
2. Redeploy generated Modelfile and model card artifacts for last passing version.
3. Re-run `release_gate.py` against rollback version metrics.
4. Keep fallback mode enabled until IBM backend health returns.
