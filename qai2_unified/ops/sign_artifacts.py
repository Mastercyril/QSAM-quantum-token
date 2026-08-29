import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_path = Path(args.output).resolve()
    digest_map = {}
    for file_path in sorted(input_dir.glob("*")):
        if file_path.is_file() and file_path.resolve() != output_path:
            digest_map[file_path.name] = sha256_file(file_path)

    key = os.environ.get("QAI2_ARTIFACT_SIGNING_KEY", "")
    if not key:
        raise SystemExit("QAI2_ARTIFACT_SIGNING_KEY is required for artifact signing.")
    signature = hmac.new(key.encode(), json.dumps(digest_map, sort_keys=True).encode(), hashlib.sha256).hexdigest()

    payload = {
        "algorithm": "sha256",
        "files": digest_map,
        "signature_hmac_sha256": signature,
        "signature_present": True,
    }
    output_path.write_text(json.dumps(payload, indent=2))
    print(f"Wrote artifact manifest: {output_path}")


if __name__ == "__main__":
    main()
