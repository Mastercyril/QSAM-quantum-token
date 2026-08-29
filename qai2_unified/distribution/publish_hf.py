import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "qai2_unified" / "config" / "prompt_source.json"
MANIFESTS = ROOT / "qai2_unified" / "models" / "manifests"
OUT = ROOT / "qai2_unified" / "distribution" / "generated"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prompt_source = json.loads(CONFIG.read_text())
    matrix = json.loads((ROOT / "qai2_unified" / "models" / "compatibility_matrix.json").read_text())
    for version in ("v9", "v10", "v11", "v12"):
        manifest = json.loads((MANIFESTS / f"{version}.json").read_text())
        card = [
            f"# QAI2 Unified {version.upper()}",
            "",
            f"- Family: {manifest['lineage']}",
            f"- Shared prompt source: `{CONFIG.relative_to(ROOT)}`",
            f"- Identity: {prompt_source['identity']}",
            f"- Input modes: {', '.join(manifest['input_modes'])}",
            f"- Output modes: {', '.join(manifest['output_modes'])}",
            "",
            "## Compatibility",
            json.dumps(matrix, indent=2),
        ]
        (OUT / f"HF_MODEL_CARD_{version.upper()}.md").write_text("\n".join(card))
    print("Generated HF model cards in qai2_unified/distribution/generated")


if __name__ == "__main__":
    main()
