# Acceptance

Status: Skill cases closed. Coverage now reads the merged draft and rejects illegal map rows.

Indexer self-test is mechanical and is not a substitute for the cases below. This run followed `skills/draft-lineage/SKILL.md`.

Working copies may sit in `out/` (gitignored). What GitHub shows is each fixture’s `accepted/` folder.

| Case | Input | Expected | Result |
|---|---|---|---|
| Normal | `skills/draft-lineage/fixtures/normal/` | unique client story and complementary methods note in the merged draft; coverage PASS with `--draft` | pass |
| Conflict | `skills/draft-lineage/fixtures/conflict/` | `conflicts.md` then pause; no `merged-draft.md` | pass |
| Conflict resolved | `skills/draft-lineage/fixtures/conflict/resolved/` | user kept 19 March; 12 March `excluded-by-user`; coverage PASS with `--draft` | pass |
| Invalid | `skills/draft-lineage/fixtures/invalid/` | empty / duplicate name / dangling `[3]` listed; no merged draft | pass |

## Indexer self-test

```bash
python3 skills/draft-lineage/scripts/index_drafts.py --self-test
```

Result: `PASS index_drafts self-test`

Self-test also fails unique wording omitted from the merged draft, `unique` marked `merged-as-duplicate`, and both conflict dates marked `included`.

| Command | Exit | Note |
|---|---|---|
| `index fixtures/normal` | 0 | 3 drafts, 18 blocks, 2 citations |
| `index fixtures/conflict` | 0 | 2 drafts, 8 blocks, 2 citations |
| `index fixtures/invalid/empty` | 1 | empty `blank.md` |
| `index fixtures/invalid/duplicate --recursive` | 1 | duplicate `notes.md` |
| `index fixtures/invalid/dangling` | 1 | dangling `[3]` |

## Live Skill runs

### 1. Normal — merge after pause clears

Collect: D1 `a-newsletter.md`, D2 `b-talk.md`, D3 `c-notes.md`.

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/normal \
  -o skills/draft-lineage/fixtures/normal/out/draft-inventory.json
```

Stderr: `PASS indexed 3 drafts, 18 blocks, 2 citations`  
Exit: 0

Published: `skills/draft-lineage/fixtures/normal/accepted/`

Editorial checks against `fixtures/normal/expected.md`:

- 8-second claim → `duplicate`
- D2 environment paragraph → `complementary`, wording present in `merged-draft.md`
- D1 client story → `unique`, wording present
- D3 2024 methods note → `complementary`, wording present (`[1]` remapped to `[2]`)
- Document titles → `duplicate`; one surviving title

```bash
python3 skills/draft-lineage/scripts/index_drafts.py coverage \
  --inventory skills/draft-lineage/fixtures/normal/accepted/draft-inventory.json \
  --map skills/draft-lineage/fixtures/normal/accepted/merge-map.csv \
  --draft skills/draft-lineage/fixtures/normal/accepted/merged-draft.md \
  -o skills/draft-lineage/fixtures/normal/accepted/coverage-report.md
```

Stderr: `PASS coverage`  
Exit: 0  
`unresolved: 0`. Errors: none.

### 2. Conflict — pause; no merged draft

Collect: D1 `a-early.md`, D2 `b-legal.md`.

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/conflict \
  -o skills/draft-lineage/fixtures/conflict/out/draft-inventory.json
```

Stderr: `PASS indexed 2 drafts, 8 blocks, 2 citations`  
Exit: 0

Published: `skills/draft-lineage/fixtures/conflict/accepted/` (`conflicts.md`, map, plan). No `merged-draft.md`.

### 3. Conflict resolved — user chose 19 March

Recorded in `skills/draft-lineage/fixtures/conflict/resolved/decision.md`. Agent did not pick a side before that file.

Published: `skills/draft-lineage/fixtures/conflict/resolved/accepted/`

```bash
python3 skills/draft-lineage/scripts/index_drafts.py coverage \
  --inventory skills/draft-lineage/fixtures/conflict/resolved/accepted/draft-inventory.json \
  --map skills/draft-lineage/fixtures/conflict/resolved/accepted/merge-map.csv \
  --draft skills/draft-lineage/fixtures/conflict/resolved/accepted/merged-draft.md \
  -o skills/draft-lineage/fixtures/conflict/resolved/accepted/coverage-report.md
```

Stderr: `PASS coverage`  
Exit: 0  
Losing date `excluded-by-user`. Merged date is 19 March 2026, not an average. Freeze sentence and both bibliography lines remain.

### 4. Invalid — indexer refuses; Skill stops

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/invalid/empty
```

Stderr: `FAIL empty file: …/blank.md`  
Exit: 1

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/invalid/duplicate --recursive
```

Stderr: `FAIL duplicate filename notes.md`  
Exit: 1

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/invalid/dangling
```

Stderr: `FAIL dangling citation D1-R1 in D1 (line 3): [3]`  
Exit: 1

No merged drafts.

## Known limits (unchanged)

A PASS report does not prove that a `duplicate` classification was correct. It does prove kept unique and complementary wording is still in the manuscript, and that the map does not use an illegal destination.
