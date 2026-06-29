#!/usr/bin/env python3
"""Validate catalog data, generated views, manifest, and examples."""

from __future__ import annotations

import csv
import datetime
import importlib.util
import json
import pathlib
import re
import subprocess
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

# LLM contract: these constants intentionally mirror
# schemas/selected-paper.schema.json so validation has no optional dependency.
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
VALID_CLAIM_SCOPES = {
    "paper metadata",
    "accepted-paper listing",
    "company research page",
    "implementation interpretation source",
}
SCHEMA_TERM_FIELDS = ("repo_db_translation",)
URL_RE = re.compile(r"^https://")
LAST_VERIFIED_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
BACKTICK_IDENTIFIER_RE = re.compile(r"`([a-z][a-z0-9_]*)`")


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
    # LLM contract: validate the committed repository surface, not whatever
    # scratch files happen to exist in a contributor's checkout.
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
    return {ROOT / "docs" / "paper-notes" / f"{slugify(record['company'])}.md" for record in records}


def obsolete_paper_note_paths(records: list[dict[str, Any]]) -> list[pathlib.Path]:
    # LLM contract: docs/paper-notes is generated catalog surface. Extra tracked
    # notes are stale public pages and must fail validation.
    expected = expected_paper_note_paths(records)
    obsolete: list[pathlib.Path] = []
    for rel_path in iter_repo_files():
        path = ROOT / rel_path
        if path.parent == ROOT / "docs" / "paper-notes" and path.suffix == ".md" and path not in expected:
            obsolete.append(path)
    return sorted(obsolete)


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


def load_generator_module(errors: list[str]) -> Any | None:
    # Import the generator so validation checks the same sort/projection contract
    # that `make generate` uses.
    spec = importlib.util.spec_from_file_location("generate_catalog", ROOT / "scripts" / "generate_catalog.py")
    if spec is None or spec.loader is None:
        error(errors, "could not import scripts/generate_catalog.py")
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
            if not isinstance(obj, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", obj):
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
                else:
                    try:
                        datetime.date.fromisoformat(last_verified)
                    except ValueError:
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
    # Ask the generator for manifest expectations instead of duplicating its
    # planned-output logic here.
    module = load_generator_module(errors)
    if module is None:
        return None
    outputs = module.build_outputs(records)
    expected_manifest = json.loads(outputs[ROOT / "manifest.json"])
    return sorted(expected_manifest.get("files", []))


def validate_manifest(records: list[dict[str, Any]], errors: list[str], expected_files: list[str] | None = None) -> None:
    manifest = load_json(ROOT / "manifest.json")
    if manifest.get("canonical_data") != "data/selected_papers.json":
        error(errors, "manifest canonical_data must be data/selected_papers.json")
    if manifest.get("row_count") != len(records):
        error(errors, "manifest row_count does not match catalog length")
    if manifest.get("companies") != [record["company"] for record in records]:
        error(errors, "manifest companies do not match generated catalog order")
    # LLM contract: compare manifest files against the generator's planned
    # repository surface, not raw checkout contents.
    actual_files = expected_files if expected_files is not None else iter_repo_files()
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
    for path in obsolete_paper_note_paths(records):
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


def ddl_table_names(ddl: str) -> set[str]:
    return set(re.findall(r"\bcreate\s+table\s+([a-z][a-z0-9_]*)\b", ddl, flags=re.IGNORECASE))


def ddl_schema_identifiers(ddl: str) -> set[str]:
    identifiers = set(ddl_table_names(ddl))
    # LLM contract: catalog schema terms may name DDL tables or columns.
    # Do not silently allow aliases like `model_cost` when the DDL says `model_costs`.
    for _table_name, body in re.findall(
        r"\bcreate\s+table\s+([a-z][a-z0-9_]*)\s*\((.*?)\n\);",
        ddl,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        for raw_line in body.splitlines():
            line = raw_line.split("--", 1)[0].strip().rstrip(",")
            if not line:
                continue
            name = line.split(None, 1)[0]
            if name in {"constraint", "primary", "foreign", "unique", "check"}:
                continue
            if re.fullmatch(r"[a-z][a-z0-9_]*", name):
                identifiers.add(name)
    return identifiers


def validate_schema_objects(records: list[dict[str, Any]], errors: list[str]) -> None:
    ddl = (ROOT / "docs" / "repo-db-schema.sql").read_text(encoding="utf-8")
    tables = ddl_table_names(ddl)
    # first_schema_objects names starter tables, not prose aliases.
    objects = {obj for record in records for obj in record["first_schema_objects"]}
    missing = sorted(objects - tables)
    if missing:
        error(errors, f"catalog schema objects missing from DDL: {missing}")


def validate_catalog_schema_terms(records: list[dict[str, Any]], errors: list[str]) -> None:
    ddl = (ROOT / "docs" / "repo-db-schema.sql").read_text(encoding="utf-8")
    identifiers = ddl_schema_identifiers(ddl)
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
    module = load_generator_module(errors)
    if module is None:
        return
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
        sorted_records = records
        if all(isinstance(record, dict) for record in records):
            module = load_generator_module(errors)
            if module is not None:
                # Derived files are generated from sorted records even when the
                # canonical JSON was edited in append order.
                sorted_records = module.sort_records(records)
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
