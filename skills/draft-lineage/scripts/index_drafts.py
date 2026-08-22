#!/usr/bin/env python3
"""Number draft blocks and citations; check that every ID has a destination."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from pathlib import Path

DESTINATIONS = frozenset(
    {
        "included",
        "merged-as-duplicate",
        "superseded-with-evidence",
        "excluded-by-user",
        "unresolved",
    }
)
MAP_FIELDS = ("source_id", "kind", "relation", "destination", "paired_ids", "notes")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^```")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")
FOOTNOTE_USE_RE = re.compile(r"\[\^([^\]]+)\]")
NUMERIC_DEF_RE = re.compile(r"^\[(\d+)\][:.\s]\s*(.*)$")
MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
NUMERIC_USE_RE = re.compile(r"(?<!!)\[(\d+)\](?!\()")
DRAFT_SUFFIXES = {".md", ".txt", ".markdown"}
SKIP_NAMES = {"expected.md", "readme.md"}

# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def is_draft_file(path: Path) -> bool:
    return (
        path.is_file()
        and path.suffix.lower() in DRAFT_SUFFIXES
        and path.name.lower() not in SKIP_NAMES
    )


def discover_files(root: Path, recursive: bool) -> list[Path]:
    if recursive:
        found = [p for p in root.rglob("*") if is_draft_file(p)]
    else:
        found = [p for p in root.iterdir() if is_draft_file(p)]
    return sorted(found, key=lambda p: (p.name.lower(), str(p).lower()))


def validate_paths(files: list[Path]) -> list[str]:
    errors: list[str] = []
    if len(files) < 2:
        errors.append(f"need 2–6 draft files, found {len(files)}")
    if len(files) > 6:
        errors.append(f"need 2–6 draft files, found {len(files)}")
    names: dict[str, list[str]] = {}
    for path in files:
        names.setdefault(path.name, []).append(str(path))
        if path.stat().st_size == 0 or not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty file: {path}")
    for name, paths in names.items():
        if len(paths) > 1:
            errors.append("duplicate filename {}: {}".format(name, ", ".join(paths)))
    return errors


# ---------------------------------------------------------------------------
# Block and citation indexing
# ---------------------------------------------------------------------------


def split_units(text: str) -> list[tuple[str, str, int]]:
    """Return (kind, body, start_line) units in document order.

    kind is heading, paragraph, or code.
    """
    lines = text.splitlines()
    units: list[tuple[str, str, int]] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if FENCE_RE.match(line.strip()):
            start = i + 1
            chunk = [line]
            i += 1
            while i < n and not FENCE_RE.match(lines[i].strip()):
                chunk.append(lines[i])
                i += 1
            if i < n:
                chunk.append(lines[i])
                i += 1
            units.append(("code", "\n".join(chunk).strip(), start))
            continue
        heading = HEADING_RE.match(line)
        if heading:
            units.append(("heading", heading.group(2).strip(), i + 1))
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        start = i + 1
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not HEADING_RE.match(lines[i]) and not FENCE_RE.match(lines[i].strip()):
            buf.append(lines[i])
            i += 1
        units.append(("paragraph", "\n".join(buf).strip(), start))
    return units


def index_blocks(draft_id: str, text: str) -> list[dict]:
    blocks: list[dict] = []
    section = 0
    para = 0
    for kind, body, line in split_units(text):
        if kind == "heading":
            section += 1
            para = 1
            block_kind = "heading"
        elif kind == "code":
            if section == 0:
                section = 1
            para += 1
            block_kind = "code"
        else:
            if section == 0:
                section = 1
            para += 1
            block_kind = "paragraph"
        blocks.append(
            {
                "id": f"{draft_id}-S{section}-P{para}",
                "draft": draft_id,
                "kind": block_kind,
                "line": line,
                "text": body,
            }
        )
    return blocks


def index_citations(draft_id: str, text: str) -> list[dict]:
    defined_footnotes: set[str] = set()
    defined_numeric: set[str] = set()
    for raw in text.splitlines():
        stripped = raw.strip()
        fn = FOOTNOTE_DEF_RE.match(stripped)
        if fn:
            defined_footnotes.add(fn.group(1))
        num = NUMERIC_DEF_RE.match(stripped)
        if num:
            defined_numeric.add(num.group(1))

    citations: list[dict] = []
    serial = 0
    in_fence = False
    for line_no, raw in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(raw.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = raw.strip()
        if FOOTNOTE_DEF_RE.match(stripped) or NUMERIC_DEF_RE.match(stripped):
            continue
        for match in MD_LINK_RE.finditer(raw):
            serial += 1
            citations.append(
                {
                    "id": f"{draft_id}-R{serial}",
                    "draft": draft_id,
                    "kind": "link",
                    "marker": match.group(2).strip(),
                    "text": match.group(1).strip(),
                    "line": line_no,
                    "resolved": True,
                }
            )
        for match in FOOTNOTE_USE_RE.finditer(raw):
            serial += 1
            marker = match.group(1)
            citations.append(
                {
                    "id": f"{draft_id}-R{serial}",
                    "draft": draft_id,
                    "kind": "footnote",
                    "marker": marker,
                    "text": match.group(0),
                    "line": line_no,
                    "resolved": marker in defined_footnotes,
                }
            )
        scratch = MD_LINK_RE.sub(" ", raw)
        scratch = FOOTNOTE_USE_RE.sub(" ", scratch)
        for match in NUMERIC_USE_RE.finditer(scratch):
            serial += 1
            marker = match.group(1)
            citations.append(
                {
                    "id": f"{draft_id}-R{serial}",
                    "draft": draft_id,
                    "kind": "numeric",
                    "marker": marker,
                    "text": match.group(0),
                    "line": line_no,
                    "resolved": marker in defined_numeric,
                }
            )
    return citations


def build_inventory(root: Path, recursive: bool) -> dict:
    files = discover_files(root, recursive=recursive)
    errors = validate_paths(files)
    drafts: list[dict] = []
    blocks: list[dict] = []
    citations: list[dict] = []
    if not errors:
        for index, path in enumerate(files, start=1):
            draft_id = f"D{index}"
            text = path.read_text(encoding="utf-8")
            drafts.append(
                {
                    "id": draft_id,
                    "path": str(path),
                    "filename": path.name,
                }
            )
            blocks.extend(index_blocks(draft_id, text))
            citations.extend(index_citations(draft_id, text))
        for cite in citations:
            if not cite["resolved"]:
                errors.append(
                    "dangling citation {} in {} (line {}): {}".format(
                        cite["id"], cite["draft"], cite["line"], cite["text"]
                    )
                )
    return {
        "root": str(root),
        "drafts": drafts,
        "blocks": blocks,
        "citations": citations,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------


def read_map(path: Path) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "source_id" not in reader.fieldnames or "destination" not in reader.fieldnames:
            return [], ["merge map must include source_id and destination columns"]
        for line_no, raw in enumerate(reader, start=2):
            source_id = (raw.get("source_id") or "").strip()
            destination = (raw.get("destination") or "").strip()
            if not source_id:
                errors.append(f"empty source_id at map line {line_no}")
                continue
            if destination not in DESTINATIONS:
                errors.append(f"unknown destination {destination!r} for {source_id}")
            rows.append(
                {
                    "source_id": source_id,
                    "kind": (raw.get("kind") or "").strip(),
                    "relation": (raw.get("relation") or "").strip(),
                    "destination": destination,
                    "paired_ids": (raw.get("paired_ids") or "").strip(),
                    "notes": (raw.get("notes") or "").strip(),
                }
            )
    seen: set[str] = set()
    for row in rows:
        if row["source_id"] in seen:
            errors.append(f"duplicate map row for {row['source_id']}")
        seen.add(row["source_id"])
    return rows, errors


def coverage_report(inventory: dict, map_rows: list[dict], map_errors: list[str]) -> tuple[str, int]:
    block_ids = [block["id"] for block in inventory["blocks"]]
    mapped = {row["source_id"]: row for row in map_rows}
    missing = [block_id for block_id in block_ids if block_id not in mapped]
    extra = [row["source_id"] for row in map_rows if row["source_id"] not in set(block_ids)]
    unresolved = [row["source_id"] for row in map_rows if row["destination"] == "unresolved"]
    dangling = [cite["id"] for cite in inventory["citations"] if not cite["resolved"]]
    errors = list(inventory.get("errors") or []) + list(map_errors)
    if missing:
        errors.append("unmapped blocks: " + ", ".join(missing))
    if extra:
        errors.append("map rows with unknown source_id: " + ", ".join(extra))
    if unresolved:
        errors.append("unresolved: " + ", ".join(unresolved))
    if dangling:
        errors.append("dangling citations: " + ", ".join(dangling))

    counts: dict[str, int] = {name: 0 for name in sorted(DESTINATIONS)}
    for row in map_rows:
        if row["destination"] in counts:
            counts[row["destination"]] += 1

    status = "FAIL" if errors else "PASS"
    lines = [
        f"# Coverage report — {status}",
        "",
        f"- drafts: {len(inventory.get('drafts') or [])}",
        f"- source blocks: {len(block_ids)}",
        f"- mapped blocks: {len(map_rows)}",
        f"- citations: {len(inventory.get('citations') or [])}",
        f"- unresolved: {len(unresolved)}",
        "",
        "## Destinations",
        "",
    ]
    for name, count in counts.items():
        lines.append(f"- `{name}`: {count}")
    lines.extend(["", "## Errors", ""])
    if errors:
        for item in errors:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines), 1 if errors else 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _write(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def self_test() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "ok"
        root.mkdir()
        _write(
            root / "a-old.md",
            "# Sleep\n\nAverage focus lasts 8 seconds [1].\n\n"
            "A client moved the phone out of the bedroom.\n\n"
            "[1]: Example Study, 2019.\n",
        )
        _write(
            root / "b-talk.md",
            "# Attention\n\nEnvironment design beats willpower.\n\n"
            "Average focus lasts 8 seconds.\n",
        )
        inventory = build_inventory(root, recursive=False)
        ids = [block["id"] for block in inventory["blocks"]]
        if inventory["errors"]:
            failures.append(f"clean pair should index: {inventory['errors']}")
        if inventory["drafts"][0]["id"] != "D1" or inventory["drafts"][1]["id"] != "D2":
            failures.append("draft IDs should follow sorted filenames")
        if "D1-S1-P1" not in ids or "D1-S1-P3" not in ids:
            failures.append(f"expected heading and unique paragraph IDs, got {ids}")
        cites = [cite["id"] for cite in inventory["citations"]]
        if "D1-R1" not in cites:
            failures.append(f"expected citation IDs, got {cites}")
        if any(not cite["resolved"] for cite in inventory["citations"]):
            failures.append("numeric [1] with a definition should resolve")

        skip_root = Path(tmp) / "skip"
        skip_root.mkdir()
        _write(skip_root / "a.md", "# A\n\nHi.\n")
        _write(skip_root / "b.md", "# B\n\nHi.\n")
        _write(skip_root / "expected.md", "# Not a draft\n\nIgnored.\n")
        skip_inv = build_inventory(skip_root, recursive=False)
        if skip_inv["errors"] or [d["filename"] for d in skip_inv["drafts"]] != ["a.md", "b.md"]:
            failures.append("expected.md must not be indexed as a draft")

        empty_root = Path(tmp) / "empty"
        empty_root.mkdir()
        _write(empty_root / "a.md", "# A\n\nHi.\n")
        _write(empty_root / "b.md", "")
        empty_inv = build_inventory(empty_root, recursive=False)
        if not any("empty file" in item for item in empty_inv["errors"]):
            failures.append("empty file must fail indexing")

        dup_root = Path(tmp) / "dup"
        (dup_root / "one").mkdir(parents=True)
        (dup_root / "two").mkdir()
        _write(dup_root / "one" / "notes.md", "# One\n\nBody.\n")
        _write(dup_root / "two" / "notes.md", "# Two\n\nBody.\n")
        dup_inv = build_inventory(dup_root, recursive=True)
        if not any("duplicate filename" in item for item in dup_inv["errors"]):
            failures.append("duplicate filenames must fail indexing")

        dang_root = Path(tmp) / "dang"
        dang_root.mkdir()
        _write(dang_root / "a.md", "# A\n\nClaim [3].\n")
        _write(dang_root / "b.md", "# B\n\nOther.\n")
        dang_inv = build_inventory(dang_root, recursive=False)
        if not any("dangling citation" in item for item in dang_inv["errors"]):
            failures.append("numeric [3] without a definition must fail")

        map_path = Path(tmp) / "map.csv"
        with map_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=MAP_FIELDS)
            writer.writeheader()
            for block in inventory["blocks"]:
                writer.writerow(
                    {
                        "source_id": block["id"],
                        "kind": block["kind"],
                        "relation": "unique" if block["id"] == "D1-S1-P3" else "duplicate",
                        "destination": "included",
                        "paired_ids": "",
                        "notes": "",
                    }
                )
        rows, map_errors = read_map(map_path)
        report, code = coverage_report(inventory, rows, map_errors)
        if code != 0:
            failures.append(f"complete map should pass coverage:\n{report}")

        bad_map = Path(tmp) / "bad-map.csv"
        with bad_map.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=MAP_FIELDS)
            writer.writeheader()
            writer.writerow(
                {
                    "source_id": inventory["blocks"][0]["id"],
                    "kind": "heading",
                    "relation": "unique",
                    "destination": "unresolved",
                    "paired_ids": "",
                    "notes": "",
                }
            )
        rows, map_errors = read_map(bad_map)
        report, code = coverage_report(inventory, rows, map_errors)
        if code == 0 or "unmapped blocks" not in report or "unresolved:" not in report:
            failures.append("incomplete unresolved map must fail coverage")

    if failures:
        print("FAIL index_drafts self-test")
        for item in failures:
            print(f"  {item}")
        return 1
    print("PASS index_drafts self-test")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_index(args: argparse.Namespace) -> int:
    root = Path(args.drafts_dir).expanduser().resolve()
    if not root.is_dir():
        print(f"FAIL not a directory: {root}", file=sys.stderr)
        return 1
    inventory = build_inventory(root, recursive=args.recursive)
    payload = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    if inventory["errors"]:
        if args.output:
            Path(args.output).write_text(payload, encoding="utf-8")
        for item in inventory["errors"]:
            print(f"FAIL {item}", file=sys.stderr)
        return 1
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    print(
        f"PASS indexed {len(inventory['drafts'])} drafts, "
        f"{len(inventory['blocks'])} blocks, {len(inventory['citations'])} citations",
        file=sys.stderr,
    )
    return 0


def cmd_coverage(args: argparse.Namespace) -> int:
    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    rows, map_errors = read_map(Path(args.map))
    report, code = coverage_report(inventory, rows, map_errors)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report if report.endswith("\n") else report + "\n")
    status = "FAIL" if code else "PASS"
    print(f"{status} coverage", file=sys.stderr)
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")

    index_p = sub.add_parser("index", help="assign stable IDs to drafts, blocks, and citations")
    index_p.add_argument("drafts_dir")
    index_p.add_argument("-o", "--output")
    index_p.add_argument("--recursive", action="store_true")

    cov_p = sub.add_parser("coverage", help="fail unless every source ID has a destination")
    cov_p.add_argument("--inventory", required=True)
    cov_p.add_argument("--map", required=True)
    cov_p.add_argument("-o", "--output")

    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.command == "index":
        return cmd_index(args)
    if args.command == "coverage":
        return cmd_coverage(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
