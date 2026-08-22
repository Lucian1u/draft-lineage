---
name: draft-lineage
description: >
  Merge 2–6 related human drafts of the same subject into one traceable manuscript.
  Use when the user uploads or points to multiple overlapping articles, chapters,
  notes, or reports and asks to merge, reconcile, combine, or produce one canonical
  draft. Also trigger on “合稿”, “多稿合卷”, “merge these drafts”, or “which parts
  are unique”. Do not use for git merges, PDF concatenation, blank-page writing,
  or comparing two linear versions of the same file.
---

# Draft Lineage

Turn a family of existing drafts into one manuscript only after every block and citation has a destination.

Read [references/merge-contract.md](references/merge-contract.md) before classifying anything.
Run numbering and coverage with [scripts/index_drafts.py](scripts/index_drafts.py). Do not let the model declare “nothing was lost.”

## Inputs

- 2–6 UTF-8 `.md` or `.txt` files
- Optional: intended reader, structure to keep, terms that must not change, which draft is later

Refuse scanned PDFs, images, and audio. Refuse a single file.

## Outputs

Write these next to the drafts, in an `out/` directory unless the user names another path:

| File | When |
|---|---|
| `draft-inventory.json` | After indexing |
| `merge-map.csv` | After classification, before any merged prose |
| `conflicts.md` | After classification |
| `synthesis-plan.md` | After classification |
| `merged-draft.md` | Only after pause rules clear |
| `coverage-report.md` | After the merged draft |

## Six steps

1. **Collect.** Copy or read the drafts. Label them D1… by sorted filename. If the user states a later draft, record that as a hint, not as a verdict.
2. **Index.** `python3 scripts/index_drafts.py index <drafts-dir> -o out/draft-inventory.json`  
   Stop if the command exits non-zero.
3. **Classify.** Using the inventory IDs, assign each block one relation from the contract. Fill `merge-map.csv` (`source_id,kind,relation,destination,paired_ids,notes`). Write `conflicts.md` and `synthesis-plan.md`.
4. **Pause.** If the contract says stop, stop. Show the conflicts and any unique blocks proposed for deletion. Wait for an explicit decision on each item. Do not produce `merged-draft.md` first.
5. **Merge.** After the map has no `unresolved` rows that the contract forbids, write `merged-draft.md`. Every fact, number, quotation, and citation must trace to an inventory ID.
6. **Cover.** `python3 scripts/index_drafts.py coverage --inventory out/draft-inventory.json --map out/merge-map.csv -o out/coverage-report.md`  
   If coverage fails, the merge is not done.

## Stop conditions

- Indexer reports empty files, duplicate filenames, or dangling citations
- Any `conflict` is still `unresolved`
- Any `unique` block would be dropped without `excluded-by-user`
- Coverage reports a missing destination or `unresolved: N` where N > 0

## What this skill does not do

- Write from a blank page
- Fetch facts from the web
- Decide which side of a conflict is true
- Polish style before coverage passes
- Treat Word compare / line diff as the job
