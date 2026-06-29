"""Generated catalog surface planning and rendering helpers."""

from __future__ import annotations

import csv
import io
import json
import pathlib
import re
import subprocess
from typing import Any

from catalog_contract import priority_rank, source_label

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "selected_papers.json"

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


def sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # LLM contract: this is the canonical generated-view order. Validators
    # must use this helper instead of reinterpreting raw JSON order.
    return sorted(
        records,
        key=lambda row: (
            priority_rank(row.get("priority")),
            row.get("company", ""),
            row.get("theme", ""),
        ),
    )


def load_catalog() -> list[dict[str, Any]]:
    with CATALOG_PATH.open(encoding="utf-8") as handle:
        records = json.load(handle)
    return sort_records(records)


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
    )


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
            # Keep provenance fields visible in generated docs so claims can be
            # audited without re-opening the canonical JSON.
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


def paper_note_path(record: dict[str, Any]) -> pathlib.Path:
    return ROOT / "docs" / "paper-notes" / f"{slugify(record['company'])}.md"


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
    # README is partially hand-written; generation may only replace the marked
    # catalog table region.
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
    # LLM contract: manifest membership is Git-tracked files only. Do not
    # replace this with a filesystem walk; untracked local files are machine noise.
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return sorted(path for path in result.stdout.splitlines() if (ROOT / path).is_file())


def expected_paper_note_paths(records: list[dict[str, Any]]) -> set[pathlib.Path]:
    return {paper_note_path(record) for record in records}


def obsolete_paper_note_paths(records: list[dict[str, Any]]) -> list[pathlib.Path]:
    # LLM contract: generated paper notes are one-to-one with current catalog
    # companies. A renamed/removed company must not leave a stale tracked note.
    expected = expected_paper_note_paths(records)
    obsolete: list[pathlib.Path] = []
    for rel_path in iter_repo_files():
        path = ROOT / rel_path
        if path.parent == ROOT / "docs" / "paper-notes" and path.suffix == ".md" and path not in expected:
            obsolete.append(path)
    return sorted(obsolete)


def manifest_text(records: list[dict[str, Any]], files: list[str]) -> str:
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
        "files": files,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def planned_file_list(outputs: dict[pathlib.Path, str], obsolete_paths: list[pathlib.Path]) -> list[str]:
    # The manifest describes the post-generation committed surface: current
    # tracked files, plus planned outputs, minus obsolete generated notes.
    files = set(iter_repo_files())
    files.difference_update(path.relative_to(ROOT).as_posix() for path in obsolete_paths)
    files.update(path.relative_to(ROOT).as_posix() for path in outputs)
    files.add("manifest.json")
    return sorted(files)


def build_outputs(records: list[dict[str, Any]]) -> dict[pathlib.Path, str]:
    obsolete_paths = obsolete_paper_note_paths(records)
    # Build all non-manifest projections first; manifest.json depends on the
    # complete planned output set.
    outputs: dict[pathlib.Path, str] = {
        ROOT / "data" / "selected_papers.csv": csv_text(records),
        ROOT / "docs" / "curated-table.md": curated_table_text(records),
        ROOT / "docs" / "source-links.md": source_links_text(records),
        ROOT / "docs" / "topic-map.md": topic_map_text(records),
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
        outputs[paper_note_path(record)] = paper_note_text(record)
    outputs[ROOT / "manifest.json"] = manifest_text(records, planned_file_list(outputs, obsolete_paths))
    return outputs


def expected_manifest_files(records: list[dict[str, Any]]) -> list[str]:
    outputs = build_outputs(records)
    expected_manifest = json.loads(outputs[ROOT / "manifest.json"])
    return sorted(expected_manifest.get("files", []))


def stale_output_paths(outputs: dict[pathlib.Path, str]) -> list[pathlib.Path]:
    mismatches: list[pathlib.Path] = []
    for path, expected in sorted(outputs.items()):
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            mismatches.append(path.relative_to(ROOT))
    return mismatches


def stale_generated_view_paths(records: list[dict[str, Any]]) -> list[pathlib.Path]:
    outputs = build_outputs(records)
    return stale_output_paths(outputs)
