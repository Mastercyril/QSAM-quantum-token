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
    digest_map = {}
    for file_path in sorted(input_dir.glob("*")):
        if file_path.is_file():
            digest_map[file_path.name] = sha256_file(file_path)

    key = os.environ.get("QAI2_ARTIFACT_SIGNING_KEY", "")
    signature = ""
    if key:
        signature = hmac.new(key.encode(), json.dumps(digest_map, sort_keys=True).encode(), hashlib.sha256).hexdigest()

    payload = {
        "algorithm": "sha256",
        "files": digest_map,
        "signature_hmac_sha256": signature,
        "signature_present": bool(signature),
    }
    Path(args.output).write_text(json.dumps(payload, indent=2))
    print(f"Wrote artifact manifest: {args.output}")


if __name__ == "__main__":
    main()
