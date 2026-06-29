#!/usr/bin/env python3
"""Generate deterministic catalog views from data/selected_papers.json."""

from __future__ import annotations

import argparse
import sys

from catalog_surface import (
    ROOT,
    build_outputs,
    load_catalog,
    obsolete_paper_note_paths,
    stale_output_paths,
)


def run(check: bool) -> int:
    records = load_catalog()
    outputs = build_outputs(records)
    obsolete_paths = obsolete_paper_note_paths(records)
    mismatches = []
    if check:
        mismatches = stale_output_paths(outputs)
        mismatches.extend(path.relative_to(ROOT) for path in obsolete_paths)
    else:
        for path, expected in sorted(outputs.items()):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
        # LLM contract: generation owns generated notes, so obsolete tracked
        # notes are removed instead of preserved in manifest.json.
        for path in obsolete_paths:
            path.unlink()

    if mismatches:
        print("Generated files are out of date:", file=sys.stderr)
        for path in mismatches:
            print(f"  {path}", file=sys.stderr)
        print("Run `make generate` and commit the resulting changes.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
