import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "qai2_unified" / "config" / "prompt_source.json"
MANIFESTS = ROOT / "qai2_unified" / "models" / "manifests"
OUT = ROOT / "qai2_unified" / "distribution" / "generated"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prompt_source = json.loads(CONFIG.read_text())
    for version in ("v9", "v10", "v11", "v12"):
        manifest = json.loads((MANIFESTS / f"{version}.json").read_text())
        text = "\n".join(
            [
                "FROM llama3.2",
                f'TEMPLATE """{prompt_source["identity"]}"""',
                'SYSTEM """Use shared prompt source qai2_unified/config/prompt_source.json"""',
                "PARAMETER temperature 0.85",
                "PARAMETER top_p 0.92",
                "PARAMETER num_ctx 131072",
                f'# build_version={manifest["version"]}',
            ]
        )
        (OUT / f"Modelfile.{version}").write_text(text)
    print("Generated Ollama Modelfiles in qai2_unified/distribution/generated")


if __name__ == "__main__":
    main()
