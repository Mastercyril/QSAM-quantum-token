"""
qai2_unified/distribution/launch_local.py
------------------------------------------
Repo-owned launch path for QAI2 models via a locally installed Ollama binary.

Instead of relying on the hosted ollama.com service this script:
  1. Locates the Ollama binary on the current machine (PATH / common install
     locations on Linux/macOS/Windows).
  2. Picks the highest available generated Modelfile from
     qai2_unified/distribution/generated/.
  3. Runs `ollama create` to register the model, then `ollama run` to start it.

Usage
-----
  # Normal interactive launch (requires ollama installed):
  python qai2_unified/distribution/launch_local.py

  # Choose a specific version:
  python qai2_unified/distribution/launch_local.py --version v12

  # CI / dry-run – validates paths and prints the commands that would be run:
  python qai2_unified/distribution/launch_local.py --dry-run
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "qai2_unified" / "distribution" / "generated"
MODEL_TAG_PREFIX = "qai2-local"
VERSIONS = ("v12", "v11", "v10", "v9")

FALLBACK_PATHS = [
    "/usr/local/bin/ollama",
    "/usr/bin/ollama",
    str(Path.home() / ".local" / "bin" / "ollama"),
    # Windows default
    str(Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"),
]


def find_ollama() -> str | None:
    """Return the path to the ollama binary or None if not found."""
    found = shutil.which("ollama")
    if found:
        return found
    for candidate in FALLBACK_PATHS:
        if Path(candidate).is_file():
            return candidate
    return None


def resolve_modelfile(version: str | None) -> tuple[str, Path]:
    """Return (version_tag, modelfile_path) for the chosen or newest available version."""
    versions_to_try = [version] if version else list(VERSIONS)
    for v in versions_to_try:
        path = GENERATED / f"Modelfile.{v}"
        if path.exists():
            return v, path
    raise FileNotFoundError(
        f"No Modelfile found in {GENERATED} for versions {versions_to_try}. "
        "Run `python qai2_unified/distribution/publish_ollama.py` first."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Repo-owned local launch for QAI2 via Ollama (no ollama.com dependency)."
    )
    parser.add_argument(
        "--version",
        choices=list(VERSIONS),
        default=None,
        help="Model version to launch (default: newest available).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them (safe for CI).",
    )
    args = parser.parse_args()

    ollama_bin = find_ollama()
    if not ollama_bin:
        if args.dry_run:
            print("[dry-run] ollama binary not found – skipping execution check (CI only).")
        else:
            sys.exit(
                "ERROR: ollama binary not found on this machine.\n"
                "Install from https://ollama.com/download or package your own binary "
                "into the repo at qai2_unified/bin/ollama."
            )

    version, modelfile = resolve_modelfile(args.version)
    model_tag = f"{MODEL_TAG_PREFIX}:{version}"

    # ollama_bin is a valid string here: if it were None and --dry-run was not
    # set, sys.exit() would have been called above.
    effective_bin = ollama_bin if ollama_bin else "<ollama-not-found>"
    create_cmd = [effective_bin, "create", model_tag, "-f", str(modelfile)]
    run_cmd = [effective_bin, "run", model_tag]

    if args.dry_run:
        print(f"[dry-run] Modelfile : {modelfile}")
        print(f"[dry-run] Model tag : {model_tag}")
        print(f"[dry-run] Create cmd: {' '.join(create_cmd)}")
        print(f"[dry-run] Run cmd   : {' '.join(run_cmd)}")
        print("[dry-run] OK – repo-owned launch path validated.")
        return

    # At this point ollama_bin is guaranteed non-None (sys.exit would have fired).
    print(f"Registering model {model_tag} from {modelfile} …")
    subprocess.run(create_cmd, check=True)

    print(f"Launching {model_tag} …")
    subprocess.run(run_cmd, check=True)


if __name__ == "__main__":
    main()
