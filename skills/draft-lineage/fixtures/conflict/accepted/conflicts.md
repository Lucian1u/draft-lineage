# Conflicts — conflict fixture

Skill stops here. No `merged-draft.md`. The agent does not pick “the later file” and does not average 12 March and 19 March.

## Open items

### C1. Public launch date

| | D1 `a-early.md` | D2 `b-legal.md` |
|---|---|---|
| Block | D1-S1-P2 | D2-S1-P2 |
| Claim | The public launch is 12 March 2026 [1]. | The public launch is 19 March 2026 [1]. |
| Citation | D1-R1 → D1-S1-P4 Launch calendar, product ops, 2 February 2026 | D2-R1 → D2-S1-P4 Outside counsel email, 8 March 2026 |
| Relation | `conflict` | `conflict` |
| Destination | `unresolved` | `unresolved` |

Both dates cannot be true. Need an explicit choice of one date, or an explicit decision to keep both as unresolved alternatives. A compromise date is not in either draft.

### C2. Ban on announcing 12 March

- D2-S1-P3: “Do not announce an earlier date. The 12 March option is not approved.”
- Relation: `conflict` with D1-S1-P2. Destination: `unresolved`.
- This block is not evidence that D2 supersedes D1. `evolved` requires the later wording to name or clearly replace the earlier one inside the drafts; file dates are not that evidence.

## Unique blocks waiting on C1

- D1-S1-P3 (engineering freeze the Friday before “that date”) is `unique` and mapped `included`. It cannot be placed until C1 is decided. It is not proposed for deletion.

Wait for an explicit decision on C1 and C2 before writing `merged-draft.md`.
