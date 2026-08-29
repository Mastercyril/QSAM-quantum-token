import argparse
import re
from pathlib import Path


PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)api[_-]?key\\s*[:=]\\s*['\\\"][A-Za-z0-9_\\-]{16,}['\\\"]"),
    re.compile(r"(?i)secret\\s*[:=]\\s*['\\\"][A-Za-z0-9_\\-]{16,}['\\\"]"),
    re.compile(r"(?i)token\\s*[:=]\\s*['\\\"][A-Za-z0-9_\\-]{16,}['\\\"]"),
]


def scan(path: Path) -> list[str]:
    findings = []
    content = path.read_text(errors="ignore")
    for i, line in enumerate(content.splitlines(), start=1):
        if any(p.search(line) for p in PATTERNS):
            findings.append(f"{path}:{i}:{line.strip()}")
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    all_findings = []
    for p in args.paths:
        path = Path(p)
        if path.is_file():
            all_findings.extend(scan(path))
    if all_findings:
        for finding in all_findings:
            print(finding)
        raise SystemExit(1)
    print("No secret patterns found.")


if __name__ == "__main__":
    main()
