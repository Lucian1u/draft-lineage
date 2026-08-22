# AGENTS.md

Repository files are the source of continuity across conversations.
Do not recover the product from chat history.

## Read in this order

1. `docs/AGENTS.md`
2. `docs/STATUS.md`
3. `skills/draft-lineage/SKILL.md`
4. `skills/draft-lineage/references/merge-contract.md`
5. Files named by the current STATUS item

The original task sheet `A-20260822-02_多稿合卷_副本.md` is provenance. It is not required to continue.

## Source of truth

| Concern | File |
|---|---|
| When to trigger, six steps, stop conditions | `skills/draft-lineage/SKILL.md` |
| Relation types and destinations | `skills/draft-lineage/references/merge-contract.md` |
| Stable IDs and coverage | `skills/draft-lineage/scripts/index_drafts.py` |
| Public introduction | `README.md` |
| What the next conversation does | `docs/STATUS.md` |
| Whether a full run passed | `acceptance.md` |

Do not copy the relation table into `SKILL.md` or `README.md`.

## Rules

- One conversation does the current STATUS item only.
- Do not re-research GitHub or the web unless STATUS says so.
- Do not write recording scripts or social posts until `acceptance.md` records three passing cases.
- An explicit user change to the contract is written into the repository before it is implemented.
