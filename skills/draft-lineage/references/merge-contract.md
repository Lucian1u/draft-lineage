# Merge contract

This file is the only source of relation types and destination states.
`SKILL.md` points here. Do not copy the lists into other files.

## Scope

Apply this contract to 2–6 UTF-8 Markdown or plain-text drafts on the same subject.
The drafts are a family, not linear versions of one file.

The agent classifies. The script numbers blocks, rejects illegal map rows, and checks that kept unique and complementary wording still appears in the merged draft. The script does not decide whether two blocks are the same claim.

## Relation types

Classify each source block against the rest of the family. A block gets exactly one relation.

| Type | Meaning | Allowed automatic next step |
|---|---|---|
| `duplicate` | Wording differs, same job in the argument | May fold into one surviving sentence |
| `complementary` | Each draft adds a piece of the same claim | May combine |
| `evolved` | A later draft explicitly replaces an earlier wording | May keep the later wording only if the map records the earlier ID as superseded |
| `conflict` | Conclusions, dates, numbers, or terms cannot all be true | Must pause |
| `unique` | Appears in only one draft | Must keep, or pause if exclusion is proposed |

`unique` applies to claims, examples, quotations, and citations. A heading that only names the source draft may be `duplicate` (same job: title the manuscript). Do not classify three document titles as `unique` in order to force all three onto the merged page.

Do not upgrade `unique` to `duplicate` to make a smoother draft.
Do not downgrade `conflict` to `evolved` because one file looks newer.
File dates are not evidence of `evolved`. The later wording must name or clearly replace the earlier one.

## Destination states

Every source block ID from `draft-inventory.json` appears in `merge-map.csv` with exactly one destination.

| Destination | Meaning | Who may set it |
|---|---|---|
| `included` | Survives in the merged draft | Agent, after classification |
| `merged-as-duplicate` | Folded into another included block | Agent, only for `duplicate` |
| `superseded-with-evidence` | Replaced by an `evolved` block whose map row names this ID | Agent, only for `evolved` |
| `excluded-by-user` | Left out because the user said so | User only |
| `unresolved` | No decision yet | Default until the user decides |

The agent must not set `excluded-by-user` on a `unique` block.
The agent must not set `included` on a `conflict` block by picking a side or writing a compromise sentence.

Illegal rows. Coverage fails when any of these are true:

- `merged-as-duplicate` on a row whose relation is not `duplicate`
- `superseded-with-evidence` on a row whose relation is not `evolved`
- `unique` with destination `merged-as-duplicate` or `superseded-with-evidence`
- `unique` with a destination other than `included`, `excluded-by-user`, or `unresolved`
- `conflict` with destination `merged-as-duplicate` or `superseded-with-evidence`
- `conflict` with destination `included` unless every ID in `paired_ids` has destination `excluded-by-user` (the user picked this side)

After the user names a side, the chosen `conflict` row may be `included` and the losing `conflict` row `excluded-by-user`. Then merge.

## Pause rules

Stop after `merge-map.csv`, `conflicts.md`, and `synthesis-plan.md`.
Do not write `merged-draft.md` while any of these are true:

- any block is `conflict` and still `unresolved`
- any `unique` block is proposed for exclusion
- any citation in the inventory is unresolved
- any source block is missing from the map

After the user decides, update the map, then write the merged draft, then run coverage.

## Merged draft rules

Facts, numbers, quotations, and citations in `merged-draft.md` must come from included or merged source blocks already in the inventory.
If a claim needs a source the drafts do not contain, write a visible placeholder. Do not invent a source.
Citation markers may be renumbered in the merged draft. The definition text must still appear.

## Coverage rules

`scripts/index_drafts.py coverage` reads the inventory, the map, and — after a merge — `merged-draft.md`. It fails when:

- a source block has no map row
- a destination is missing or unknown
- a relation is missing or unknown
- any illegal relation/destination pair above is present
- any destination is `unresolved`
- a citation marker has no matching definition in that draft
- a merge was written, but `--draft` was omitted
- a `unique` or `complementary` block with destination `included` has its source wording missing from `merged-draft.md`

Whitespace is ignored when matching. For a bibliography line (`[1]: …` or `[^id]: …`), only the definition text after the marker must appear.

`duplicate` survivors may be rephrased. `merged-as-duplicate` and `superseded-with-evidence` rows are not required to appear verbatim.

A passing coverage report does not prove that a `duplicate` classification was correct. It does prove that kept unique and complementary wording is still in the manuscript, and that the map does not use an illegal destination.
