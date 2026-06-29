#!/usr/bin/env python3
"""Generate deterministic catalog views from data/selected_papers.json."""

from __future__ import annotations

import argparse
import csv
import io
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "selected_papers.json"

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}

TOPIC_DECISION_RULES = {
    "Snowflake": "Store every AI operation as queryable data.",
    "Microsoft": "Models propose; benchmarks decide.",
    "Databricks": "Generated files are materialized views.",
    "AWS": "Preserve relational compatibility before custom sharding.",
    "Google": "Paths change; stable IDs and hashes endure.",
    "Alibaba": "Connect execution, lineage, and retrieval.",
    "ByteDance": "Model repo knowledge as a typed graph.",
    "IBM": "Measure quality and system cost together.",
    "Oracle": "Keep raw documents and relational projections.",
    "Neo4j": "Add graph DB after multi-hop workload evidence.",
    "Cockroach Labs": "Use distributed SQL for HA metadata services.",
    "Tencent": "Classify heterogeneous workloads early.",
}

PRACTICAL_GROUPS = {
    "Must implement early": [
        "Google-style stable file identity.",
        "Databricks-style generated artifact freshness.",
        "Snowflake/Microsoft-style AI logging and validation.",
        "Alibaba/ByteDance-style graph and lineage tables.",
        "Oracle-style document-to-relational projection.",
    ],
    "Implement after workload evidence": [
        "Neo4j mirror for graph traversal.",
        "AWS-style router/shard layer.",
        "Cockroach-style consensus metadata ranges.",
        "Tencent-style heterogeneous distributed routing.",
    ],
    "Evaluate continuously": [
        "IBM/RAGPerf-style RAG benchmark suite.",
        "Microsoft-style optimizer/benchmark gates for LLM proposals.",
    ],
}

SOURCE_TYPE_LABELS = {
    "acm_doi": "ACM DOI",
    "amazon_science": "primary / Amazon Science",
    "arxiv": "primary / arXiv",
    "company_blog": "company blog / paper announcement",
    "company_research": "company research page",
    "google_research": "primary / Google Research",
    "sigmod_industry_listing": "SIGMOD 2026 Industry listing",
    "supporting_arxiv": "supporting benchmark / arXiv",
}


def load_catalog() -> list[dict[str, Any]]:
    with CATALOG_PATH.open(encoding="utf-8") as handle:
        records = json.load(handle)
    return sorted(
        records,
        key=lambda row: (
            PRIORITY_ORDER.get(row.get("priority"), 99),
            row.get("company", ""),
            row.get("theme", ""),
        ),
    )


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
    )


def source_label(source: dict[str, Any]) -> str:
    if source.get("type"):
        return str(source["type"])
    return SOURCE_TYPE_LABELS.get(str(source.get("source_type", "")), str(source.get("source_type", "")))


def source_link(source: dict[str, Any], include_label: bool = False) -> str:
    title = source["title"]
    url = source.get("source_url") or source["url"]
    if include_label:
        return f"[{title}]({url}) `{source_label(source)}`"
    return f"[{title}]({url})"


def key_papers_csv(sources: list[dict[str, Any]]) -> str:
    parts = []
    for source in sources:
        url = source.get("source_url") or source["url"]
        parts.append(f"{source['title']} <{url}>")
    return "; ".join(parts)


def schema_objects(objects: list[str]) -> str:
    return ", ".join(f"`{obj}`" for obj in objects)


def csv_text(records: list[dict[str, Any]]) -> str:
    output = io.StringIO()
    fieldnames = [
        "company",
        "theme",
        "adoptable_idea",
        "why_it_matters",
        "repo_db_translation",
        "first_schema_objects",
        "do_now",
        "do_later",
        "watch_out",
        "priority",
        "key_papers",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow(
            {
                "company": record["company"],
                "theme": record["theme"],
                "adoptable_idea": record["adoptable_idea"],
                "why_it_matters": record["why_it_matters"],
                "repo_db_translation": record["repo_db_translation"],
                "first_schema_objects": "; ".join(record["first_schema_objects"]),
                "do_now": record["do_now"],
                "do_later": record["do_later"],
                "watch_out": record["watch_out"],
                "priority": record["priority"],
                "key_papers": key_papers_csv(record["key_papers"]),
            }
        )
    return output.getvalue()


def curated_table_text(records: list[dict[str, Any]]) -> str:
    lines = [
        "# Curated Table",
        "",
        "| Company | Adoptable idea | Sources | Repo / DB translation | First schema objects | Caveat |",
        "|---|---|---|---|---|---|",
    ]
    for record in records:
        sources = "<br>".join(source_link(source, include_label=True) for source in record["key_papers"])
        lines.append(
            "| "
            + " | ".join(
                [
                    f"**{record['company']}**",
                    record["adoptable_idea"],
                    sources,
                    record["repo_db_translation"],
                    schema_objects(record["first_schema_objects"]),
                    record["watch_out"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Notes on source types",
            "",
            "- Source labels are generated from `data/selected_papers.json`.",
            "- Factual paper metadata comes from the linked source record.",
            "- Repo / DB translations are implementation interpretations maintained by this repository.",
        ]
    )
    return "\n".join(lines) + "\n"


def source_links_text(records: list[dict[str, Any]]) -> str:
    lines = [
        "# Source Links",
        "",
        "This file is generated from `data/selected_papers.json`.",
        "Each entry separates factual source metadata from this repository's implementation interpretation.",
        "",
    ]
    for record in records:
        lines.append(f"## {record['company']}")
        lines.append("")
        for source in record["key_papers"]:
            url = source.get("source_url") or source["url"]
            extras = [
                f"type: `{source.get('source_type', '')}`",
                f"venue/track: `{source.get('venue_or_track', '')}`",
                f"id: `{source.get('doi_or_arxiv', '')}`",
                f"verified: `{source.get('last_verified', '')}`",
                f"claim scope: `{source.get('claim_scope', '')}`",
            ]
            lines.append(f"- [{source['title']}]({url}) — {source_label(source)}; " + "; ".join(extras))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def topic_map_text(records: list[dict[str, Any]]) -> str:
    lines = [
        "# Topic Map",
        "",
        "This file is generated from `data/selected_papers.json`.",
        "",
        "| Theme | Companies / papers | Repository database objects | Decision rule |",
        "|---|---|---|---|",
    ]
    for record in records:
        paper_names = ", ".join(source["title"] for source in record["key_papers"])
        lines.append(
            "| "
            + " | ".join(
                [
                    record["theme"],
                    f"{record['company']}: {paper_names}",
                    schema_objects(record["first_schema_objects"]),
                    TOPIC_DECISION_RULES.get(record["company"], record["adoptable_idea"]),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Practical grouping")
    lines.append("")
    for title, items in PRACTICAL_GROUPS.items():
        lines.append(f"### {title}")
        lines.append("")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def paper_note_text(record: dict[str, Any]) -> str:
    lines = [
        f"# {record['company']}",
        "",
        "## Theme",
        "",
        record["theme"],
        "",
        "## Adoptable idea",
        "",
        record["adoptable_idea"],
        "",
        "## Why it matters",
        "",
        record["why_it_matters"],
        "",
        "## Key papers / links",
        "",
    ]
    for source in record["key_papers"]:
        lines.append(f"- {source_link(source)} — {source_label(source)}")
    lines.extend(
        [
            "",
            "## Repo / DB translation",
            "",
            record["repo_db_translation"],
            "",
            "## First schema objects",
            "",
        ]
    )
    for obj in record["first_schema_objects"]:
        lines.append(f"- `{obj}`")
    lines.extend(
        [
            "",
            "## Do now",
            "",
            record["do_now"],
            "",
            "## Do later",
            "",
            record["do_later"],
            "",
            "## Caveat",
            "",
            record["watch_out"],
            "",
            "## Priority",
            "",
            record["priority"],
        ]
    )
    return "\n".join(lines) + "\n"


def readme_table_text(records: list[dict[str, Any]]) -> str:
    lines = [
        "| Company | Adoptable idea | Key papers / source links | Repo / DB translation |",
        "|---|---|---|---|",
    ]
    for record in records:
        sources = "<br>".join(source_link(source) for source in record["key_papers"])
        lines.append(
            "| "
            + " | ".join(
                [
                    f"**{record['company']}**",
                    record["adoptable_idea"],
                    sources,
                    record["repo_db_translation"],
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def replace_region(text: str, start: str, end: str, body: str) -> str:
    pattern = re.compile(
        rf"({re.escape(start)}\n)(.*?)(\n{re.escape(end)})",
        flags=re.DOTALL,
    )
    replacement = rf"\1{body}\3"
    new_text, count = pattern.subn(replacement, text)
    if count != 1:
        raise ValueError(f"Expected one generated region bounded by {start} and {end}")
    return new_text


def iter_repo_files() -> list[str]:
    excluded_parts = {".git", "__pycache__"}
    excluded_suffixes = {".pyc", ".pyo"}
    paths: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in excluded_parts for part in rel.parts):
            continue
        if path.suffix in excluded_suffixes:
            continue
        if path.name == ".DS_Store":
            continue
        paths.append(rel.as_posix())
    return sorted(paths)


def manifest_text(records: list[dict[str, Any]]) -> str:
    existing: dict[str, Any] = {}
    manifest_path = ROOT / "manifest.json"
    if manifest_path.exists():
        with manifest_path.open(encoding="utf-8") as handle:
            existing = json.load(handle)
    payload = {
        "name": existing.get("name", "Awesome-Database-papers-2026-06"),
        "created_at": existing.get("created_at", "2026-06-29T08:06:45Z"),
        "description": existing.get(
            "description",
            "Curated database-system papers and implementation playbook for repository metadata DB design.",
        ),
        "source_scope": existing.get("source_scope", "Links and summaries only; no paper PDFs redistributed."),
        "canonical_data": "data/selected_papers.json",
        "row_count": len(records),
        "companies": [record["company"] for record in records],
        "files": iter_repo_files(),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def build_outputs(records: list[dict[str, Any]]) -> dict[pathlib.Path, str]:
    outputs: dict[pathlib.Path, str] = {
        ROOT / "data" / "selected_papers.csv": csv_text(records),
        ROOT / "docs" / "curated-table.md": curated_table_text(records),
        ROOT / "docs" / "source-links.md": source_links_text(records),
        ROOT / "docs" / "topic-map.md": topic_map_text(records),
        ROOT / "manifest.json": manifest_text(records),
    }

    readme_path = ROOT / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")
    outputs[readme_path] = replace_region(
        readme_text,
        "<!-- catalog:readme-table:start -->",
        "<!-- catalog:readme-table:end -->",
        readme_table_text(records),
    )

    for record in records:
        outputs[ROOT / "docs" / "paper-notes" / f"{slugify(record['company'])}.md"] = paper_note_text(record)
    return outputs


def run(check: bool) -> int:
    records = load_catalog()
    outputs = build_outputs(records)
    mismatches: list[pathlib.Path] = []
    for path, expected in sorted(outputs.items()):
        if check:
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != expected:
                mismatches.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    if mismatches:
        print("Generated files are out of date:", file=sys.stderr)
        for path in mismatches:
            print(f"  {path}", file=sys.stderr)
        print("Run `make generate` and commit the resulting changes.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
