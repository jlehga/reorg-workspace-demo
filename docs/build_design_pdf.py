#!/usr/bin/env python3
"""Build docs/design.pdf from docs/design.md (pandoc HTML + WeasyPrint)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "design.md"
CSS = ROOT / "docs" / "design-pdf.css"
OUT = ROOT / "docs" / "design.pdf"
DIST = ROOT / "dist" / "design.pdf"


def main() -> int:
    if not MD.is_file():
        print(f"Missing {MD}", file=sys.stderr)
        return 1
    if not CSS.is_file():
        print(f"Missing {CSS}", file=sys.stderr)
        return 1

    html = subprocess.check_output(
        [
            "pandoc",
            str(MD),
            "-f",
            "markdown",
            "-t",
            "html5",
            "--standalone",
            "--metadata",
            "title=Design Doc: Agentic-Driven Reorg Case",
            "-c",
            CSS.name,
        ],
        cwd=str(MD.parent),
        text=True,
    )

    # Inline CSS so WeasyPrint does not depend on relative link resolution.
    css_text = CSS.read_text(encoding="utf-8")
    html = html.replace(
        f'<link rel="stylesheet" href="{CSS.name}" />',
        f"<style>\n{css_text}\n</style>",
        1,
    )
    # Drop pandoc's default title block duplication if present; h1 from md is enough.
    html = html.replace('<header id="title-block-header">', '<header id="title-block-header" style="display:none">')

    try:
        from weasyprint import HTML
    except ImportError:
        print("weasyprint is required: pip install weasyprint", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(MD.parent)).write_pdf(str(OUT))

    DIST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, DIST)
    print(f"Wrote {OUT}")
    print(f"Wrote {DIST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
