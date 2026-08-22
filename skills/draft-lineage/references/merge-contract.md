# Merge contract

This file is the only source of relation types and destination states.
`SKILL.md` points here. Do not copy the lists into other files.

## Scope

Apply this contract to 2–6 UTF-8 Markdown or plain-text drafts on the same subject.
The drafts are a family, not linear versions of one file.

The agent classifies. The script only numbers blocks and checks that every ID has a destination.

## Relation types

Classify each source block against the rest of the family. A block gets exactly one relation.

| Type | Meaning | Allowed automatic next step |
|---|---|---|
| `duplicate` | Wording differs, same job in the argument | May fold into one surviving sentence |
| `complementary` | Each draft adds a piece of the same claim | May combine |
| `evolved` | A later draft explicitly replaces an earlier wording | May keep the later wording only if the map records the earlier ID as superseded |
| `conflict` | Conclusions, dates, numbers, or terms cannot all be true | Must pause |
| `unique` | Appears in only one draft | Must keep, or pause if exclusion is proposed |

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

## Coverage rules

`scripts/index_drafts.py coverage` reads the inventory and the map. It fails when:

- a source block has no map row
- a destination is missing or unknown
- any destination is `unresolved`
- a citation marker has no matching definition in that draft

A passing coverage report is mechanical ID accounting. It does not prove that a `duplicate` classification was correct.
