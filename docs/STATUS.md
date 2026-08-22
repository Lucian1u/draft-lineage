# Status

## Current conversation

Next: 录屏分镜 / 口播 / 主帖.

Public remote: https://github.com/Lucian1u/draft-lineage  
Install: `Lucian1u/draft-lineage` (`skills/draft-lineage`).

Do not re-run the three Skill fixtures unless a fixture or the contract changes.
Do not create a GitHub Release unless asked.

## Done

- Open-source layout: README, MIT, plugin manifest, Codex `agents/openai.yaml`
- README figures: `assets/readme/hero.svg`, `flow.svg`, `proof.svg`
- `merge-contract.md` owns relation types and destinations
- `SKILL.md` owns trigger, six steps, stop conditions
- `index_drafts.py` index + coverage + `--self-test` (PASS)
- Fixture inputs for normal, conflict, invalid
- Invalid fixtures rejected by the indexer as specified
- Live Skill run of three fixtures recorded in `acceptance.md`
  - `fixtures/normal/out/`: map, plan, merged draft, coverage `unresolved: 0`
  - `fixtures/conflict/out/`: `conflicts.md` then stop; no `merged-draft.md`
  - `fixtures/invalid/*`: indexer exit 1; no merged draft
- Public GitHub remote `Lucian1u/draft-lineage` (MIT)
- GitHub About and README copy: 多份同题旧稿 → 可追溯成稿；先编号，冲突先停，确认后再合稿

## Known limits

- Coverage is ID accounting. It cannot catch a wrong `duplicate`.
