# Contributing

This skill is for a family of existing drafts. Changes should keep that job small.

## Do not

- Auto-resolve `conflict`
- Auto-delete `unique`
- Let the model declare coverage
- Duplicate the relation table outside `references/merge-contract.md`
- Add PDF, Word, or web-research scope to the minimum version

## Do

1. Add a fixture that fails today, with the expected stop or destination.
2. If the change is mechanical (IDs, empty files, dangling citations, illegal map rows, missing kept wording), extend `scripts/index_drafts.py --self-test`.
3. If the change is editorial (a new relation edge case), add it to `merge-contract.md` once, then point `SKILL.md` at it.
4. Run:

```bash
python3 skills/draft-lineage/scripts/index_drafts.py --self-test
python3 skills/draft-lineage/scripts/index_drafts.py index skills/draft-lineage/fixtures/invalid/dangling
```

The second command should exit non-zero.

## Pull requests

Include the original sentences, why the current contract mis-handles them, and whether the pause gate still fires.
