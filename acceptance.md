# Acceptance

Status: three Skill cases closed on 2026-08-22.

Indexer self-test is mechanical and is not a substitute for the three cases below. This run followed `skills/draft-lineage/SKILL.md`: collect → index → classify → pause → merge (only if pause clears) → cover.

Outputs live next to each fixture in `out/` (gitignored). Commands were run from the repository root.

| Case | Input | Expected | Result |
|---|---|---|---|
| Normal | `skills/draft-lineage/fixtures/normal/` | `duplicate`, `complementary`, `unique`; unique example and new source in the merged draft; coverage `unresolved: 0` | pass |
| Conflict | `skills/draft-lineage/fixtures/conflict/` | `conflicts.md` then pause; no `merged-draft.md` | pass |
| Invalid | `skills/draft-lineage/fixtures/invalid/` | empty / duplicate name / dangling `[3]` listed; no merged draft | pass |

## Indexer self-test

```bash
python3 skills/draft-lineage/scripts/index_drafts.py --self-test
```

Result: `PASS index_drafts self-test`

| Command | Exit | Note |
|---|---|---|
| `index fixtures/normal` | 0 | 3 drafts, 18 blocks, 2 citations |
| `index fixtures/conflict` | 0 | 2 drafts, 8 blocks, 2 citations |
| `index fixtures/invalid/empty` | 1 | empty `blank.md` |
| `index fixtures/invalid/duplicate --recursive` | 1 | duplicate `notes.md` |
| `index fixtures/invalid/dangling` | 1 | dangling `[3]` |

## Live Skill runs

### 1. Normal — merge after pause clears

Collect: D1 `a-newsletter.md`, D2 `b-talk.md`, D3 `c-notes.md` (sorted filenames).

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/normal \
  -o skills/draft-lineage/fixtures/normal/out/draft-inventory.json
```

Stderr: `PASS indexed 3 drafts, 18 blocks, 2 citations`  
Exit: 0

Classify (agent, using inventory IDs and `references/merge-contract.md`):

| Path | Role |
|---|---|
| `skills/draft-lineage/fixtures/normal/out/merge-map.csv` | 18 block rows |
| `skills/draft-lineage/fixtures/normal/out/conflicts.md` | no `conflict`; no unique proposed for deletion |
| `skills/draft-lineage/fixtures/normal/out/synthesis-plan.md` | structure before prose |

Editorial checks against `fixtures/normal/expected.md`:

- 8-second claim D1-S2-P2 / D2-S3-P2 / D3-S2-P2 → `duplicate` (survivor D1-S2-P2 `included`; others `merged-as-duplicate`)
- D2-S2-P2 environment paragraph → `complementary`, `included`
- D1-S3-P2 client story → `unique`, `included`, present in `merged-draft.md`
- D3-S3-P2 2024 methods note → `complementary`, `included`, present in `merged-draft.md` as citation `[2]` (source D3-R1 used `[1]` in D3; remapped so it is not collapsed into D1-R1)

Pause: clear. Then:

`skills/draft-lineage/fixtures/normal/out/merged-draft.md`

```bash
python3 skills/draft-lineage/scripts/index_drafts.py coverage \
  --inventory skills/draft-lineage/fixtures/normal/out/draft-inventory.json \
  --map skills/draft-lineage/fixtures/normal/out/merge-map.csv \
  -o skills/draft-lineage/fixtures/normal/out/coverage-report.md
```

Stderr: `PASS coverage`  
Exit: 0

`coverage-report.md`:

```
# Coverage report — PASS

- drafts: 3
- source blocks: 18
- mapped blocks: 18
- citations: 2
- unresolved: 0

## Destinations

- `excluded-by-user`: 0
- `included`: 14
- `merged-as-duplicate`: 4
- `superseded-with-evidence`: 0
- `unresolved`: 0

## Errors

- none
```

`out/` after this case: `draft-inventory.json`, `merge-map.csv`, `conflicts.md`, `synthesis-plan.md`, `merged-draft.md`, `coverage-report.md`.

### 2. Conflict — pause; no merged draft

Collect: D1 `a-early.md`, D2 `b-legal.md`.

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/conflict \
  -o skills/draft-lineage/fixtures/conflict/out/draft-inventory.json
```

Stderr: `PASS indexed 2 drafts, 8 blocks, 2 citations`  
Exit: 0

Classify then stop:

| Path | Role |
|---|---|
| `skills/draft-lineage/fixtures/conflict/out/merge-map.csv` | date blocks `conflict` + `unresolved` |
| `skills/draft-lineage/fixtures/conflict/out/conflicts.md` | C1 12 March vs 19 March; C2 ban on announcing 12 March |
| `skills/draft-lineage/fixtures/conflict/out/synthesis-plan.md` | plan only; not a merge |

Did not pick “the later file”. Did not average the dates. Did not run coverage (step 6 is after a merged draft).

`skills/draft-lineage/fixtures/conflict/out/merged-draft.md` — absent.

`out/` after this case: `draft-inventory.json`, `merge-map.csv`, `conflicts.md`, `synthesis-plan.md`. No `merged-draft.md`, no `coverage-report.md`.

### 3. Invalid — indexer refuses; Skill stops

No classify, no merge. Indexer exit non-zero is the stop condition.

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/invalid/empty \
  -o skills/draft-lineage/fixtures/invalid/empty/out/draft-inventory.json
```

Stderr: `FAIL empty file: …/fixtures/invalid/empty/blank.md`  
Exit: 1  
`merged-draft.md`: absent. `out/` contains only `draft-inventory.json` (`errors` lists the empty file; `drafts` empty).

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/invalid/duplicate --recursive \
  -o skills/draft-lineage/fixtures/invalid/duplicate/out/draft-inventory.json
```

Stderr: `FAIL duplicate filename notes.md: …/dup-a/notes.md, …/dup-b/notes.md`  
Exit: 1  
`merged-draft.md`: absent. `out/` contains only `draft-inventory.json`.

```bash
python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/invalid/dangling \
  -o skills/draft-lineage/fixtures/invalid/dangling/out/draft-inventory.json
```

Stderr: `FAIL dangling citation D1-R1 in D1 (line 3): [3]`  
Exit: 1  
`merged-draft.md`: absent. Inventory records D1-R1 `resolved: false`.

## Known limits (unchanged)

Coverage is ID accounting. A PASS report does not prove that a `duplicate` classification was correct.
