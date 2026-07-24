from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    from .common import resource_path
except ImportError:
    from common import resource_path

EMPTY_WORK_DIRS = (
    "00_input/original",
    "00_input/supplementary",
    "04_real_assets/publisher_originals",
    "04_real_assets/official_originals",
    "04_real_assets/formula_renders",
    "04_real_assets/references",
    "05_visual_system/pilot",
    "06_build/scripts",
    "06_build/intermediate",
    "07_qa/rounds",
    "07_qa/renders_final",
)


def initialize_project(destination: Path, template: Path | None = None) -> Path:
    source = (template or resource_path("templates/project")).resolve()
    destination = destination.resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"Template directory does not exist: {source}")
    if destination.exists():
        raise FileExistsError(
            f"Destination already exists: {destination}. "
            "The initializer never merges into or overwrites an existing project."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    for relative in EMPTY_WORK_DIRS:
        (destination / relative).mkdir(parents=True, exist_ok=True)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a new Evidence-First PPT project from the canonical template.")
    parser.add_argument("destination", type=Path, help="New project directory; it must not already exist.")
    parser.add_argument("--template", type=Path, help="Optional alternative template directory.")
    args = parser.parse_args(argv)
    try:
        result = initialize_project(args.destination, args.template)
    except (FileNotFoundError, FileExistsError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
