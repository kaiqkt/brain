#!/usr/bin/env python3
"""Verify index.md coverage — reports notes missing from index and stale entries.

Does NOT write anything. Exit 0 always (informational only).
The AI maintains index.md content and summaries.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent.parent
INDEX_PATH = VAULT / "index.md"
IGNORED_DIRS = {"raw", ".obsidian", ".git", ".claude"}
IGNORED_ROOT_FILES = {"index.md", "CLAUDE.md"}

WIKILINK = re.compile(r"\[\[([^\]|#\\]+)(?:\\?\|[^\]]+)?\]\]")


def iter_notes() -> list[Path]:
    notes: list[Path] = []
    for path in VAULT.rglob("*.md"):
        rel_parts = path.relative_to(VAULT).parts
        if rel_parts[0] in IGNORED_DIRS:
            continue
        if len(rel_parts) == 1 and rel_parts[0] in IGNORED_ROOT_FILES:
            continue
        notes.append(path)
    return notes


def parse_index_links() -> set[str]:
    if not INDEX_PATH.exists():
        return set()
    text = INDEX_PATH.read_text(encoding="utf-8")
    return {m.group(1).strip() for m in WIKILINK.finditer(text)}


def main() -> int:
    notes = iter_notes()
    note_stems = {
        note.relative_to(VAULT).with_suffix("").as_posix()
        for note in notes
    }
    indexed = parse_index_links()

    missing_from_index = note_stems - indexed
    stale_in_index = indexed - note_stems

    if not missing_from_index and not stale_in_index:
        print(f"OK — {len(notes)} notes, index.md in sync.")
        return 0

    if missing_from_index:
        print("Notes not listed in index.md (add them):")
        for p in sorted(missing_from_index):
            print(f"  + {p}")

    if stale_in_index:
        print("Index entries with no matching note (remove them):")
        for p in sorted(stale_in_index):
            print(f"  - {p}")

    print(f"\n{len(missing_from_index)} missing, {len(stale_in_index)} stale — update index.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
