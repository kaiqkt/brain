# Brain — Personal Knowledge Vault

Maintained collaboratively. **You author. AI assists.** AI drafts on request, helps refine your drafts, makes pointed corrections, and maintains structural artifacts (index, lint). It does not auto-author content notes.

## Folder Structure

Flat top-level by life-domain. No `personal/` or `work/` wrapper.

| Folder | Intent |
|---|---|
| `calendar/daily/` | Daily notes (one file per day) |
| `calendar/events/` | Scheduled events / agenda (manual or synced from external calendar) |
| `clippings/` | Link inbox — products, articles, videos to triage |
| `notes/` | Free-form annotations, fleeting thoughts |
| `projects/` | Dev side-projects (each project = subfolder) |
| `initiatives/` | Non-tech life plans (email reorg, home design, habits) |
| `study/` | Study plans + framework deep-dives |
| `tools/dev/` | Dev runbooks, cheatsheets, configs |
| `tools/daily/` | Non-dev utilities (productivity apps, day-to-day tools) |
| `homelab/` | Server infra, self-host configs |
| `hobby/gaming/` | Gaming notes — wishlists, playthroughs, game-specific study |
| `people/` | Contact notes (one file per person) |
| `raw/` | Read-only sources to ingest. **Never modify.** |

Vault maintenance scripts live in `.claude/scripts/` (lint, reindex). They are deterministic and run by hook on `git push` — no AI required.

New top-level folders may be added when a new domain emerges (e.g. `finance/`). Do not nest by ownership.

## Language

All content in **English** — titles, body, frontmatter values, link labels. Exception: proper nouns and user-supplied quotes preserve original language.

## Naming

`snake_case` everywhere (lowercase, underscore-separated).

| Type | Pattern | Example |
|---|---|---|
| Folders | snake_case | `home_design`, `tools/dev` |
| Files | snake_case | `kotlin_coroutines.md` |
| Daily notes | ISO date | `2026-06-15.md` |
| Events | `YYYY-MM-DD_slug` | `2026-06-15_dentist.md` |
| Tags | lowercase hyphenated | `#game-design`, `#self-hosted` |

## Frontmatter

### Baseline (every note)

```yaml
---
title: "Page Title"
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Each folder may add fields. Body structure is free unless the folder defines one.

### Designated schemas

#### `calendar/daily/`

```yaml
---
title: "YYYY-MM-DD"
type: daily
date: YYYY-MM-DD
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Body: time-stamped sections. Context tag after the pipe.

```markdown
## HH:MM | context

content
```

Context examples: `personal`, `dev`, `study`, `gaming`. Pick what fits — no closed list.

#### `calendar/events/`

```yaml
---
title: "Event name"
type: event
start: YYYY-MM-DDTHH:MM
end: YYYY-MM-DDTHH:MM
location: ""
attendees: []
source: manual          # or: google, ical
external_id: ""         # set when synced from external calendar
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Future external-calendar sync (Google, etc.) writes here. Manual entries also live here. The `source` + `external_id` fields gate sync conflict resolution.

#### `people/`

```yaml
---
title: "Person Name"
tags: [people, <relationship>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Name

One-line: who this person is and their relationship to me.

## Info
- Stable facts (birthday, job, location, pets)

## Notes
- Append-only observations
```

Two sections only. No per-topic sub-sections.

#### `clippings/`

```yaml
---
title: "..."
url: "https://..."
type: link
status: inbox           # or: triaged, archived
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Body: one paragraph why this matters + any quick excerpt.

### Free-form folders

`notes/`, `projects/`, `initiatives/`, `study/`, `tools/`, `homelab/`, `hobby/` — only baseline frontmatter required. Body is free. For multi-file projects use a subfolder; entry file can be named anything (`concept.md`, `overview.md`, or just the project name).

## Links

Obsidian wiki links: `[[page_name]]` or `[[page_name|display label]]`.

## Index

`index.md` at vault root. **Auto-generated.** Do not hand-edit.

Regenerate with:

```bash
python3 .claude/scripts/reindex.py
```

Auto-runs after every `git push` via git pre-push hook.

## AI Role

- **Drafts on request** — you ask for a starting point, AI writes the skeleton.
- **Pointed corrections** — you write, AI reviews and proposes edits.
- **Structural maintenance** — AI keeps frontmatter consistent, runs lint/reindex when asked.
- **Linking suggestions** — AI proposes `[[wikilinks]]` between related notes.
- **Does not** auto-author content notes without your request.
- **Does not** modify `raw/`.

## Scripts

Deterministic checks live in `.claude/scripts/` to avoid spending AI calls on mechanical work.

| Script | Purpose |
|---|---|
| `.claude/scripts/lint.py` | Frontmatter required-fields check, filename snake_case, date format, dead wiki-links |
| `.claude/scripts/reindex.py` | Walk vault, regenerate `index.md` |

Both run automatically before every `git push` via git pre-push hook (`.claude/hooks/pre-push.sh`). Lint failure blocks the push. Reindex always runs; if `index.md` changed, the push proceeds with a warning to commit the update.

Install the hook once after `git init`:

```bash
ln -sf ../../.claude/hooks/pre-push.sh .git/hooks/pre-push
```

For AI-driven semantic checks (orphans, duplicates, stale notes) invoke the `vault-verify` skill: `/vault-verify`.

## Obsidian Plugins

Tracked in `.obsidian/` — copied from prior vault.

- **Dataview** — query notes as DB. `dataview` code blocks for dynamic lists.
- **Templater** — JS templates.
- **Tasks** — `- [ ] task 📅 YYYY-MM-DD` syntax.
- **Calendar** — daily-note calendar view. Points at `calendar/daily/`.
- **Linter** — formatting on save.
- **Obsidian Git** — auto-commit + push.
- **Table Editor** — markdown table editing.
- **Excalidraw** — embed drawings via `![[drawing.excalidraw]]`.

## Maintenance Rules

- `raw/` is read-only. Never edit.
- Lint + reindex run automatically after `git push`. Manual run: `python3 .claude/scripts/lint.py` and `python3 .claude/scripts/reindex.py`.
- Update `CLAUDE.md` when introducing a new folder, schema, or workflow.
- When a person is mentioned in a note (task, daily, project), create or link their `people/<name>.md`.
