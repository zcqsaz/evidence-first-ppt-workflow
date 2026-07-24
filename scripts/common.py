from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

TOOL_VERSION = "1.0.1"
REPO_ROOT = Path(__file__).resolve().parents[1]
SHARE_ROOT = Path(sys.prefix) / "share" / "evidence-first-ppt-workflow"


def resource_path(relative: str | Path) -> Path:
    """Locate a repository resource in editable or wheel-installed form."""
    relative = Path(relative)
    repository_candidate = REPO_ROOT / relative
    if repository_candidate.exists():
        return repository_candidate
    return SHARE_ROOT / relative


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def validate_json(instance: Any, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    messages: list[str] = []
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        messages.append(f"{location}: {error.message}")
    return messages


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def issue(severity: str, code: str, message: str, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"severity": severity, "code": code, "message": message}
    result.update({key: value for key, value in extra.items() if value is not None})
    return result


def build_report(
    tool: str,
    target: Path,
    issues: list[dict[str, Any]],
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    counts = Counter(item["severity"] for item in issues)
    return {
        "tool": tool,
        "tool_version": TOOL_VERSION,
        "generated_at": utc_now_iso(),
        "target": str(target.resolve()),
        "status": "fail" if counts["error"] else "pass",
        "summary": {
            "errors": counts["error"],
            "warnings": counts["warning"],
            "info": counts["info"],
        },
        "metrics": metrics or {},
        "issues": issues,
    }


def write_report(report: dict[str, Any], output: Path | None) -> None:
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)


def natural_key(value: str) -> list[Any]:
    import re

    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def iter_files(root: Path, suffixes: Iterable[str]) -> Iterable[Path]:
    wanted = {suffix.lower() for suffix in suffixes}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in wanted:
            yield path
