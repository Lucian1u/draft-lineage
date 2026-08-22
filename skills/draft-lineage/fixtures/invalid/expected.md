# Expected — invalid

`empty/` — indexer lists the empty file and exits non-zero.
`duplicate/` with `--recursive` — indexer lists duplicate filename `notes.md` and exits non-zero.
`dangling/` — indexer lists dangling `[3]` and exits non-zero.
None of these folders produce `merged-draft.md`.
