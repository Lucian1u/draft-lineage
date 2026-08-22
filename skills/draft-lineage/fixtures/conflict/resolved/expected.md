# Expected — conflict after the user decides

The user named 19 March 2026 (D2) and excluded 12 March 2026 (D1).
That is an explicit decision, not the agent picking “the later file.”
`merged-draft.md` may exist only after that decision.
The losing date is `excluded-by-user`. The winning date is `included` with `paired_ids` pointing at the excluded row.
Coverage with `--draft` passes. The merged date is 19 March, not an average.
