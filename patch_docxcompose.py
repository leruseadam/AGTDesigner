#!/usr/bin/env python3
"""Shim: run the real patcher at scripts/utilities/patch_docxcompose.py (docs reference this path)."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    target = root / "scripts" / "utilities" / "patch_docxcompose.py"
    if not target.is_file():
        raise SystemExit(f"Missing {target}")
    runpy.run_path(str(target), run_name="__main__")
