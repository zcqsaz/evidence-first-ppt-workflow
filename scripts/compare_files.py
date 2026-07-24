from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .common import sha256_file, utc_now_iso
except ImportError:
    from common import sha256_file, utc_now_iso


def compare_files(first: Path, second: Path) -> dict:
    first = first.resolve()
    second = second.resolve()
    result = {
        "tool": "compare_files",
        "generated_at": utc_now_iso(),
        "first": str(first),
        "second": str(second),
        "first_exists": first.is_file(),
        "second_exists": second.is_file(),
        "first_sha256": None,
        "second_sha256": None,
        "identical": False,
    }
    if first.is_file():
        result["first_sha256"] = sha256_file(first)
    if second.is_file():
        result["second_sha256"] = sha256_file(second)
    result["identical"] = bool(result["first_sha256"] and result["first_sha256"] == result["second_sha256"])
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prove that the approved PPTX and delivery copy are byte-identical.")
    parser.add_argument("approved_file", type=Path)
    parser.add_argument("delivery_copy", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    result = compare_files(args.approved_file, args.delivery_copy)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0 if result["identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
