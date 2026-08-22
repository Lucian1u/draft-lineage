<p align="center">
  <img src="assets/readme/hero.svg" alt="draft-lineage: index, map, pause, cover" width="100%">
</p>

`draft-lineage` is an Agent Skill for a narrow job: you already have 2–6 overlapping human drafts of the same subject, and you need one manuscript without silent deletes.

它不把几份旧稿直接写成一篇顺稿。它先给段落和引文编号，画出重复、互补、演进、冲突和独有，冲突处停住，等你决定之后才合稿，最后用脚本核对每个来源 ID 是否有去向。

<p align="center">
  <img src="assets/readme/flow.svg" alt="INDEX → MAP → PAUSE → MERGE → COVER" width="100%">
</p>

## 为什么不是直接让模型合稿

直接合稿通常会得到一篇读着完整的文章。缺的是证明：独有例子进了哪一节，互斥的日期有没有被平均成一个谁都没写过的数字，引文还对着原来的来源吗。

<p align="center">
  <img src="assets/readme/proof.svg" alt="Naive merge versus draft-lineage" width="100%">
</p>

| 直接合稿常见结果 | draft-lineage |
|---|---|
| 独有段落消失 | `unique` 必须进入合稿，或由你标明删除 |
| 冲突被润成“大约” | `conflict` 暂停，不写 `merged-draft.md` |
| 模型宣布没有遗漏 | `index_drafts.py coverage` 按 ID 核对 |
| 两份线性版本的 Diff | 不是这个 Skill 的工作 |

## 它产出什么

| 文件 | 作用 |
|---|---|
| `draft-inventory.json` | 稿件、段落、引文的稳定 ID |
| `merge-map.csv` | 每个 ID 的关系与去向 |
| `conflicts.md` | 必须由你决定的项 |
| `synthesis-plan.md` | 合稿结构，在写正文之前 |
| `merged-draft.md` | 仅在暂停条件清除后 |
| `coverage-report.md` | 脚本生成；`unresolved` 大于 0 则失败 |

关系类型和去向状态只定义在 [`skills/draft-lineage/references/merge-contract.md`](skills/draft-lineage/references/merge-contract.md)。

## 安装

Skill 目录是 `skills/draft-lineage/`。

Claude Code：

```bash
git clone https://github.com/Lucian1u/draft-lineage.git
cp -R draft-lineage/skills/draft-lineage ~/.claude/skills/draft-lineage
```

或把本仓库加为 plugin marketplace 后安装 `draft-lineage`。

Codex：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo Lucian1u/draft-lineage \
  --path skills/draft-lineage
```

其他兼容 [Agent Skills](https://agentskills.io/) 的工具，把 `skills/draft-lineage` 复制到该工具的 skills 目录即可。

## 使用

把 Skill 和稿件放在同一轮任务里：

```text
使用 draft-lineage，处理 fixtures/normal/ 里的三份稿。
先编号和出冲突清单，不要直接写合稿。
```

```text
使用 draft-lineage。两份稿对同一发布日给出了不同日期。
按合同暂停，等我逐项决定。
```

输入限于 2–6 个 UTF-8 Markdown 或纯文本文件。不要丢扫描 PDF。

## 脚本

编号和覆盖检查只用 Python 标准库：

```bash
python3 skills/draft-lineage/scripts/index_drafts.py --self-test

python3 skills/draft-lineage/scripts/index_drafts.py index \
  skills/draft-lineage/fixtures/normal \
  -o /tmp/draft-inventory.json

python3 skills/draft-lineage/scripts/index_drafts.py coverage \
  --inventory /tmp/draft-inventory.json \
  --map /tmp/merge-map.csv \
  -o /tmp/coverage-report.md
```

索引失败（空文件、重复文件名、悬空 `[3]`）时退出码非 0，且不得进入合稿。
覆盖检查通过只说明每个 ID 都有去向，不说明关系分类正确。

## 示例稿

| 目录 | 用来验证 |
|---|---|
| [`fixtures/normal/`](skills/draft-lineage/fixtures/normal) | 跨稿重复、互补、独有例子和新来源都进入合稿 |
| [`fixtures/conflict/`](skills/draft-lineage/fixtures/conflict) | 互斥日期必须暂停 |
| [`fixtures/invalid/`](skills/draft-lineage/fixtures/invalid) | 空文件、重名、悬空引文必须拒绝 |

完整 Agent 跑通记录见 [`acceptance.md`](acceptance.md)。三用例已关闭：正常组合稿覆盖 `unresolved: 0`，冲突组停在 `conflicts.md`，无效组在索引失败处拒绝。

## 仓库结构

```text
draft-lineage/
├── assets/readme/          hero, flow, proof
├── skills/draft-lineage/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/merge-contract.md
│   ├── scripts/index_drafts.py
│   └── fixtures/
├── docs/                   agent handoff, not product copy
├── LICENSE
└── README.md
```

## 限制

- 不从空白代写，不联网补事实。
- 不判断哪一方观点正确。
- 覆盖报告不能证明 `duplicate` 没有误判。
- 不处理 Word 修订、git 冲突或 PDF 拼接。

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。不要提交「先出合稿再让用户找错」的改法。那是本 Skill 存在的理由。

## License

[MIT](./LICENSE)
