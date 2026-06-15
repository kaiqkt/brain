---
name: vault-verify
description: >
  Verifies vault health. Runs deterministic lint (frontmatter, naming, dead links)
  and regenerates index.md, then adds AI-driven semantic checks (orphans, potential
  duplicates, stale notes). Triggers: "/vault-verify", "lint", "verifica o vault",
  "revisa o vault", "auditoria", "health check", "valida o brain". Also runs
  automatically as a git pre-push hook (deterministic checks only — the semantic
  checks need a Claude session).
---

# Skill: vault-verify

Audit the brain vault. Combines the deterministic scripts with AI-only checks that scripts cannot perform.

## Behavior

- **Read-only**. This skill never modifies content notes. It may regenerate `index.md` because that file is auto-generated.
- **Run scripts first**, before any AI reasoning, to handle the cheap mechanical checks:
  - `python3 .claude/scripts/lint.py` — frontmatter, naming, date format, dead wikilinks.
  - `python3 .claude/scripts/reindex.py` — rewrite `index.md`.
- **AI-only checks** — only the ones scripts cannot do well:
  1. **Orphan pages** — notes not linked from any other note and not the entry file of a project folder.
  2. **Potential duplicates** — notes with near-identical titles or heavy semantic overlap.
  3. **Stale notes** — `updated` more than 6 months old combined with shallow content (might be abandoned).
  4. **Language drift** — body content not in English (excluding proper nouns and quoted material).
  5. **Cross-link suggestions** — surface pairs of notes that share tags/concepts but have no link between them.
- **Merge findings** from scripts + AI into a single report.
- **Do not** apply fixes inline. After the report, ask the user which to fix; handle fixes in a follow-up turn.

## Report Format

```
## Vault Verify — YYYY-MM-DD

### Critical (push-blocking)
- path/to/file.md: dead wikilink [[xxx]]
- path/to/file.md: missing frontmatter field 'updated'

### Warnings
- path/to/file.md: orphan (no inbound links)
- path/to/file.md: stale (updated 2025-08-12, body unchanged shape)

### Info
- path/to/file.md ↔ other/file.md: potential duplicate (similar titles)
- path/to/file.md ↔ other/file.md: shared tags but no cross-link

### Stats
- Notes: X
- Folders touched: X
- Lint findings: X
- Orphans: X
- Potential duplicates: X
```

Severity guide:
- **Critical** — would break linking or fail lint; blocks pre-push.
- **Warning** — likely real problem, should fix soon.
- **Info** — opinion, accept or ignore.

## After the Report

Ask: "Encontrei X issues. Quais corrigir agora?"

If the user accepts fixes, exit this skill and apply them in a normal turn. `vault-verify` itself does not write content.
