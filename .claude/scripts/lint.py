#!/usr/bin/env python3
"""Vault lint — deterministic checks. Exits non-zero on any finding."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent.parent
IGNORED_DIRS = {"raw", ".obsidian", ".git", ".claude"}
IGNORED_ROOT_FILES = {"index.md", "CLAUDE.md"}

BASELINE_FIELDS = {"title", "tags", "created", "updated"}

SCHEMA: dict[str, dict[str, set[str]]] = {
    "calendar/daily": {
        "required": {"title", "type", "date", "tags", "created", "updated"},
        "type_values": {"daily"},
    },
    "calendar/events": {
        "required": {"title", "type", "start", "end", "source", "tags", "created", "updated"},
        "type_values": {"event"},
    },
    "people": {
        "required": {"title", "tags", "created", "updated"},
    },
    "clippings": {
        "required": {"title", "url", "type", "status", "tags", "created", "updated"},
        "type_values": {"link"},
    },
}

SNAKE_CASE = re.compile(r"^[a-z0-9_]+$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")
EVENT_FILENAME = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9_]+$")
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]")


@dataclass
class Finding:
    path: Path
    message: str

    def __str__(self) -> str:
        rel = self.path.relative_to(VAULT)
        return f"{rel}: {self.message}"


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


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return data, body


def schema_for(rel: Path) -> dict[str, set[str]] | None:
    parts = rel.parts
    for depth in (2, 1):
        key = "/".join(parts[:depth])
        if key in SCHEMA:
            return SCHEMA[key]
    return None


def check_filename(path: Path, findings: list[Finding]) -> None:
    rel = path.relative_to(VAULT)
    stem = path.stem
    parts = rel.parts

    if parts[0] == "calendar" and len(parts) > 1:
        if parts[1] == "daily":
            if not ISO_DATE.match(stem):
                findings.append(Finding(path, f"daily note must be YYYY-MM-DD, got '{stem}'"))
            return
        if parts[1] == "events":
            if not EVENT_FILENAME.match(stem):
                findings.append(Finding(path, f"event must be YYYY-MM-DD_slug, got '{stem}'"))
            return

    if not SNAKE_CASE.match(stem):
        findings.append(Finding(path, f"filename not snake_case: '{stem}'"))


def check_frontmatter(path: Path, data: dict[str, str], findings: list[Finding]) -> None:
    rel = path.relative_to(VAULT)
    schema = schema_for(rel)
    required = schema["required"] if schema else BASELINE_FIELDS

    missing = required - data.keys()
    if missing:
        findings.append(Finding(path, f"missing frontmatter fields: {sorted(missing)}"))

    if schema and "type_values" in schema:
        actual = data.get("type", "").strip('"').strip("'")
        if actual not in schema["type_values"]:
            findings.append(
                Finding(path, f"type must be one of {sorted(schema['type_values'])}, got '{actual}'")
            )

    for date_field in ("created", "updated", "date"):
        if date_field in data and date_field in required:
            value = data[date_field].strip('"').strip("'")
            if value and not ISO_DATE.match(value):
                findings.append(Finding(path, f"{date_field} must be YYYY-MM-DD, got '{value}'"))

    for dt_field in ("start", "end"):
        if dt_field in data and dt_field in required:
            value = data[dt_field].strip('"').strip("'")
            if value and not ISO_DATETIME.match(value):
                findings.append(Finding(path, f"{dt_field} must be YYYY-MM-DDTHH:MM, got '{value}'"))


def check_links(path: Path, body: str, link_index: dict[str, list[Path]], findings: list[Finding]) -> None:
    for match in WIKILINK.finditer(body):
        target = match.group(1).strip()
        if not target:
            continue
        last = target.split("/")[-1]
        if last not in link_index and target not in link_index:
            findings.append(Finding(path, f"dead wikilink: [[{target}]]"))


def build_link_index(notes: list[Path]) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for note in notes:
        stem = note.stem
        index.setdefault(stem, []).append(note)
        rel = note.relative_to(VAULT).with_suffix("")
        index.setdefault(str(rel), []).append(note)
    return index


def main() -> int:
    notes = iter_notes()
    link_index = build_link_index(notes)
    findings: list[Finding] = []

    for path in notes:
        check_filename(path, findings)
        text = path.read_text(encoding="utf-8")
        parsed = parse_frontmatter(text)
        if parsed is None:
            findings.append(Finding(path, "missing or malformed frontmatter"))
            continue
        data, body = parsed
        check_frontmatter(path, data, findings)
        check_links(path, body, link_index, findings)

    if not findings:
        print(f"OK — {len(notes)} notes, no findings.")
        return 0

    for f in findings:
        print(str(f))
    print(f"\n{len(findings)} finding(s) across {len(notes)} note(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
