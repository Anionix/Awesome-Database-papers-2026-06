#!/usr/bin/env python3
"""Validate catalog data, generated views, manifest, and examples."""

from __future__ import annotations

import csv
import json
import pathlib
import re
import sys
from typing import Any

import catalog_surface
from catalog_contract import (
    BACKTICK_IDENTIFIER_RE,
    LAST_VERIFIED_RE,
    REQUIRED_RECORD_FIELDS,
    REQUIRED_SOURCE_FIELDS,
    SCHEMA_OBJECT_RE,
    SCHEMA_TERM_FIELDS,
    URL_RE,
    VALID_CLAIM_SCOPES,
    VALID_PRIORITIES,
    is_valid_last_verified_date,
)
from sql_corpus import schema_identifiers, table_names

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "selected_papers.json"
SCHEMA_PATH = ROOT / "schemas" / "selected-paper.schema.json"


def load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


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
        # Mirrors JSON Schema `additionalProperties: false`; extra catalog keys
        # should be added deliberately, with generator/docs updates.
        extra_record_fields = sorted(set(record) - set(REQUIRED_RECORD_FIELDS))
        if extra_record_fields:
            error(errors, f"{label}: unexpected fields {extra_record_fields}")
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
            if not isinstance(obj, str) or not SCHEMA_OBJECT_RE.fullmatch(obj):
                error(errors, f"{label}: invalid schema object `{obj}`")
        for source in record.get("key_papers", []):
            if not isinstance(source, dict):
                error(errors, f"{label}: key_papers entries must be objects")
                continue
            # Mirrors JSON Schema `additionalProperties: false` for provenance
            # records, while keeping this script stdlib-only.
            extra_source_fields = sorted(set(source) - set(REQUIRED_SOURCE_FIELDS))
            if extra_source_fields:
                error(errors, f"{label}: source `{source.get('title', '?')}` unexpected fields {extra_source_fields}")
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
            # LLM contract: provenance fields are data contracts, not prose.
            # Keep these explicit checks aligned with selected-paper.schema.json.
            last_verified = source.get("last_verified")
            if isinstance(last_verified, str):
                if not LAST_VERIFIED_RE.fullmatch(last_verified):
                    error(errors, f"{label}: source `{source.get('title', '?')}` last_verified must use YYYY-MM-DD")
                elif not is_valid_last_verified_date(last_verified):
                    error(errors, f"{label}: source `{source.get('title', '?')}` last_verified must be a valid date")
            claim_scope = source.get("claim_scope")
            if isinstance(claim_scope, str) and claim_scope not in VALID_CLAIM_SCOPES:
                error(errors, f"{label}: source `{source.get('title', '?')}` claim_scope must be one of {sorted(VALID_CLAIM_SCOPES)}")
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
        error(errors, "CSV company order does not match generated catalog order")


def expected_manifest_files(records: list[dict[str, Any]], errors: list[str]) -> list[str] | None:
    # Ask the lower catalog surface for manifest expectations instead of
    # duplicating its planned-output logic here.
    return catalog_surface.expected_manifest_files(records)


def validate_manifest(records: list[dict[str, Any]], errors: list[str], expected_files: list[str] | None = None) -> None:
    manifest = load_json(ROOT / "manifest.json")
    if manifest.get("canonical_data") != "data/selected_papers.json":
        error(errors, "manifest canonical_data must be data/selected_papers.json")
    if manifest.get("row_count") != len(records):
        error(errors, "manifest row_count does not match catalog length")
    if manifest.get("companies") != [record["company"] for record in records]:
        error(errors, "manifest companies do not match generated catalog order")
    # LLM contract: compare manifest files against the catalog surface's planned
    # repository surface, not raw checkout contents.
    actual_files = expected_files if expected_files is not None else catalog_surface.iter_repo_files()
    listed_files = sorted(manifest.get("files", []))
    if listed_files != actual_files:
        missing = sorted(set(actual_files) - set(listed_files))
        extra = sorted(set(listed_files) - set(actual_files))
        error(errors, f"manifest files are stale; missing={missing}; extra={extra}")


def validate_paper_notes(records: list[dict[str, Any]], errors: list[str]) -> None:
    for record in records:
        path = catalog_surface.paper_note_path(record)
        if not path.exists():
            error(errors, f"missing paper note for {record['company']}: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith(f"# {record['company']}\n"):
            error(errors, f"paper note heading mismatch: {path.relative_to(ROOT)}")
    for path in catalog_surface.obsolete_paper_note_paths(records):
        error(errors, f"obsolete paper note: {path.relative_to(ROOT)}")


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
    # docs/source-links.md is generated. Its links must exactly reflect the
    # canonical catalog, not a hand-curated subset.
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
    tables = table_names(ddl)
    # first_schema_objects names starter tables, not prose aliases.
    objects = {obj for record in records for obj in record["first_schema_objects"]}
    missing = sorted(objects - tables)
    if missing:
        error(errors, f"catalog schema objects missing from DDL: {missing}")


def validate_catalog_schema_terms(records: list[dict[str, Any]], errors: list[str]) -> None:
    ddl = (ROOT / "docs" / "repo-db-schema.sql").read_text(encoding="utf-8")
    # LLM contract: catalog schema terms may name DDL tables or columns.
    # Do not silently allow aliases like `model_cost` when the DDL says `model_costs`.
    identifiers = schema_identifiers(ddl)
    for record in records:
        label = record["company"]
        for field in SCHEMA_TERM_FIELDS:
            value = record.get(field, "")
            if not isinstance(value, str):
                continue
            # Backticked schema-like words in public generated docs must be
            # real DDL identifiers, not approximate names.
            for term in BACKTICK_IDENTIFIER_RE.findall(value):
                if term not in identifiers:
                    error(errors, f"{label}: `{term}` in {field} is not defined by docs/repo-db-schema.sql")


def validate_generated_views(records: list[dict[str, Any]], errors: list[str]) -> None:
    for path in catalog_surface.stale_generated_view_paths(records):
        error(errors, f"generated file is stale: {path}")


def main() -> int:
    errors: list[str] = []
    validate_schema_file(errors)
    records = load_json(CATALOG_PATH)
    validate_records(records, errors)
    if isinstance(records, list):
        sorted_records = records
        if all(isinstance(record, dict) for record in records):
            # Derived files are generated from sorted records even when the
            # canonical JSON was edited in append order.
            sorted_records = catalog_surface.sort_records(records)
        validate_csv(sorted_records, errors)
        validate_manifest(sorted_records, errors, expected_manifest_files(sorted_records, errors))
        validate_paper_notes(sorted_records, errors)
        validate_examples(errors)
        validate_sources(sorted_records, errors)
        validate_schema_objects(sorted_records, errors)
        validate_catalog_schema_terms(sorted_records, errors)
        validate_generated_views(sorted_records, errors)
    if errors:
        print("Catalog validation failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("Catalog validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
