#!/usr/bin/env python3
"""Validate catalog data, generated views, manifest, and examples."""

from __future__ import annotations

import csv
import importlib.util
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "selected_papers.json"
SCHEMA_PATH = ROOT / "schemas" / "selected-paper.schema.json"

REQUIRED_RECORD_FIELDS = {
    "company": str,
    "theme": str,
    "adoptable_idea": str,
    "key_papers": list,
    "why_it_matters": str,
    "repo_db_translation": str,
    "first_schema_objects": list,
    "do_now": str,
    "do_later": str,
    "watch_out": str,
    "priority": str,
}

REQUIRED_SOURCE_FIELDS = {
    "title": str,
    "url": str,
    "type": str,
    "source_type": str,
    "source_url": str,
    "venue_or_track": str,
    "doi_or_arxiv": str,
    "last_verified": str,
    "claim_scope": str,
}

VALID_PRIORITIES = {"P0", "P1", "P2"}
URL_RE = re.compile(r"^https://")


def load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
    )


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


def error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_schema_file(errors: list[str]) -> None:
    schema = load_json(SCHEMA_PATH)
    if schema.get("type") != "array":
        error(errors, "schemas/selected-paper.schema.json must describe an array catalog")
    required = set(schema.get("items", {}).get("required", []))
    missing = set(REQUIRED_RECORD_FIELDS) - required
    if missing:
        error(errors, f"schema is missing required record fields: {sorted(missing)}")


def validate_records(records: Any, errors: list[str]) -> None:
    if not isinstance(records, list):
        error(errors, "data/selected_papers.json must be a list")
        return
    companies: set[str] = set()
    seen_sources: set[tuple[str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            error(errors, f"record {index} is not an object")
            continue
        label = record.get("company", f"record {index}")
        for field, expected_type in REQUIRED_RECORD_FIELDS.items():
            if field not in record:
                error(errors, f"{label}: missing `{field}`")
            elif not isinstance(record[field], expected_type):
                error(errors, f"{label}: `{field}` must be {expected_type.__name__}")
            elif expected_type in {str, list} and not record[field]:
                error(errors, f"{label}: `{field}` must not be empty")
        company = record.get("company")
        if isinstance(company, str):
            if company in companies:
                error(errors, f"duplicate company: {company}")
            companies.add(company)
        if record.get("priority") not in VALID_PRIORITIES:
            error(errors, f"{label}: priority must be one of {sorted(VALID_PRIORITIES)}")
        for obj in record.get("first_schema_objects", []):
            if not isinstance(obj, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", obj):
                error(errors, f"{label}: invalid schema object `{obj}`")
        for source in record.get("key_papers", []):
            if not isinstance(source, dict):
                error(errors, f"{label}: key_papers entries must be objects")
                continue
            for field, expected_type in REQUIRED_SOURCE_FIELDS.items():
                if field not in source:
                    error(errors, f"{label}: source `{source.get('title', '?')}` missing `{field}`")
                elif not isinstance(source[field], expected_type):
                    error(errors, f"{label}: source `{source.get('title', '?')}` `{field}` must be {expected_type.__name__}")
                elif field != "doi_or_arxiv" and not source[field]:
                    error(errors, f"{label}: source `{source.get('title', '?')}` `{field}` must not be empty")
            url = source.get("url")
            source_url = source.get("source_url")
            if isinstance(url, str) and not URL_RE.match(url):
                error(errors, f"{label}: source `{source.get('title', '?')}` url must be https")
            if isinstance(source_url, str) and source_url != url:
                error(errors, f"{label}: source `{source.get('title', '?')}` source_url must match url")
            key = (source.get("title", ""), source.get("url", ""))
            if key in seen_sources:
                continue
            seen_sources.add(key)


def validate_csv(records: list[dict[str, Any]], errors: list[str]) -> None:
    with (ROOT / "data" / "selected_papers.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != len(records):
        error(errors, f"CSV row count {len(rows)} does not match JSON row count {len(records)}")
    if [row["company"] for row in rows] != [record["company"] for record in records]:
        error(errors, "CSV company order does not match canonical JSON order")


def validate_manifest(records: list[dict[str, Any]], errors: list[str]) -> None:
    manifest = load_json(ROOT / "manifest.json")
    if manifest.get("canonical_data") != "data/selected_papers.json":
        error(errors, "manifest canonical_data must be data/selected_papers.json")
    if manifest.get("row_count") != len(records):
        error(errors, "manifest row_count does not match catalog length")
    if manifest.get("companies") != [record["company"] for record in records]:
        error(errors, "manifest companies do not match catalog order")
    actual_files = iter_repo_files()
    listed_files = sorted(manifest.get("files", []))
    if listed_files != actual_files:
        missing = sorted(set(actual_files) - set(listed_files))
        extra = sorted(set(listed_files) - set(actual_files))
        error(errors, f"manifest files are stale; missing={missing}; extra={extra}")


def validate_paper_notes(records: list[dict[str, Any]], errors: list[str]) -> None:
    for record in records:
        path = ROOT / "docs" / "paper-notes" / f"{slugify(record['company'])}.md"
        if not path.exists():
            error(errors, f"missing paper note for {record['company']}: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith(f"# {record['company']}\n"):
            error(errors, f"paper note heading mismatch: {path.relative_to(ROOT)}")


def validate_examples(errors: list[str]) -> None:
    for path in sorted((ROOT / "examples").glob("*.jsonl")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                error(errors, f"{path.relative_to(ROOT)}:{line_no}: invalid JSONL: {exc}")
    lineage = ROOT / "examples" / "lineage_edges_example.tsv"
    with lineage.open(encoding="utf-8") as handle:
        header = handle.readline().strip().split("\t")
    if header != ["src_node_id", "dst_node_id", "edge_type", "source", "confidence"]:
        error(errors, "examples/lineage_edges_example.tsv header changed unexpectedly")


def validate_sources(records: list[dict[str, Any]], errors: list[str]) -> None:
    canonical_urls = {source["url"] for record in records for source in record["key_papers"]}
    source_links_text = (ROOT / "docs" / "source-links.md").read_text(encoding="utf-8")
    source_links_urls = set(re.findall(r"\]\((https://[^)]+)\)", source_links_text))
    if canonical_urls != source_links_urls:
        error(errors, f"source-links URL mismatch; missing={sorted(canonical_urls - source_links_urls)}; extra={sorted(source_links_urls - canonical_urls)}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "<!-- catalog:readme-table:start -->" not in readme or "<!-- catalog:readme-table:end -->" not in readme:
        error(errors, "README must contain generated catalog table markers")
    for record in records:
        if f"**{record['company']}**" not in readme:
            error(errors, f"README missing company {record['company']}")


def validate_schema_objects(records: list[dict[str, Any]], errors: list[str]) -> None:
    ddl = (ROOT / "docs" / "repo-db-schema.sql").read_text(encoding="utf-8")
    tables = set(re.findall(r"\bcreate\s+table\s+([a-z][a-z0-9_]*)\b", ddl, flags=re.IGNORECASE))
    objects = {obj for record in records for obj in record["first_schema_objects"]}
    missing = sorted(objects - tables)
    if missing:
        error(errors, f"catalog schema objects missing from DDL: {missing}")


def validate_generated_views(records: list[dict[str, Any]], errors: list[str]) -> None:
    spec = importlib.util.spec_from_file_location("generate_catalog", ROOT / "scripts" / "generate_catalog.py")
    if spec is None or spec.loader is None:
        error(errors, "could not import scripts/generate_catalog.py")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    outputs = module.build_outputs(records)
    for path, expected in outputs.items():
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            error(errors, f"generated file is stale: {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []
    validate_schema_file(errors)
    records = load_json(CATALOG_PATH)
    validate_records(records, errors)
    if isinstance(records, list):
        validate_csv(records, errors)
        validate_manifest(records, errors)
        validate_paper_notes(records, errors)
        validate_examples(errors)
        validate_sources(records, errors)
        validate_schema_objects(records, errors)
        validate_generated_views(records, errors)
    if errors:
        print("Catalog validation failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("Catalog validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
