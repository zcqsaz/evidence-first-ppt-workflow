from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_formula(
    latex: str,
    output: Path,
    *,
    dpi: int = 300,
    font_size: float = 32,
    color: str = "#111827",
    transparent: bool = True,
    padding: float = 0.04,
) -> Path:
    expression = latex.strip()
    if not expression:
        raise ValueError("Formula source is empty.")
    if not (expression.startswith("$") and expression.endswith("$")):
        expression = f"${expression}$"
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(0.01, 0.01), dpi=dpi)
    figure.patch.set_alpha(0 if transparent else 1)
    figure.text(0, 0, expression, fontsize=font_size, color=color, usetex=False)
    try:
        figure.savefig(
            output,
            dpi=dpi,
            transparent=transparent,
            bbox_inches="tight",
            pad_inches=padding,
        )
    except Exception as exc:
        raise ValueError(f"Math rendering failed; check the LaTeX/mathtext source: {exc}") from exc
    finally:
        plt.close(figure)
    if not output.is_file() or output.stat().st_size == 0:
        raise OSError(f"Formula output was not created: {output}")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render one LaTeX/mathtext formula to a transparent high-resolution image.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--latex", help="Formula source, with or without surrounding dollar signs.")
    source.add_argument("--latex-file", type=Path, help="UTF-8 text file containing one formula.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--font-size", type=float, default=32)
    parser.add_argument("--color", default="#111827")
    parser.add_argument("--opaque", action="store_true")
    parser.add_argument("--padding", type=float, default=0.04)
    args = parser.parse_args(argv)
    try:
        latex = args.latex if args.latex is not None else args.latex_file.read_text(encoding="utf-8-sig")
        result = render_formula(
            latex,
            args.output,
            dpi=args.dpi,
            font_size=args.font_size,
            color=args.color,
            transparent=not args.opaque,
            padding=args.padding,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
