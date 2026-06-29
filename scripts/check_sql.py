#!/usr/bin/env python3
"""Static SQL sanity checks for schema, seed data, and example queries."""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DDL = ROOT / "docs" / "repo-db-schema.sql"
SEED = ROOT / "examples" / "seed.sql"
QUERIES = ROOT / "examples" / "queries.sql"
EXPLAIN = ROOT / "examples" / "explain.sql"

EXPECTED_INDEXES = {
    "artifact_dependencies_source_idx",
    "code_to_sql_edges_query_run_idx",
    "factuality_checks_eval_query_idx",
    "generated_artifacts_stale_idx",
    "graph_edges_dst_idx",
    "graph_edges_src_idx",
    "index_advice_status_idx",
    "model_costs_ai_run_idx",
    "retrieval_metrics_eval_query_idx",
    "ai_runs_unverified_idx",
}

EXPECTED_CONSTRAINTS = {
    "code_to_sql_edges_query_run_fk",
}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def table_names(sql: str) -> set[str]:
    return set(re.findall(r"\bcreate\s+table\s+([a-z][a-z0-9_]*)\b", sql, flags=re.IGNORECASE))


def index_names(sql: str) -> set[str]:
    return set(re.findall(r"\bcreate\s+(?:unique\s+)?index\s+([a-z][a-z0-9_]*)\b", sql, flags=re.IGNORECASE))


def constraint_names(sql: str) -> set[str]:
    return set(re.findall(r"\badd\s+constraint\s+([a-z][a-z0-9_]*)\b", sql, flags=re.IGNORECASE))


def referenced_tables(sql: str) -> set[str]:
    stripped_lines = []
    for line in sql.splitlines():
        stripped_lines.append(line.split("--", 1)[0])
    stripped = "\n".join(stripped_lines)
    return set(re.findall(r"\b(?:from|join|insert\s+into)\s+([a-z][a-z0-9_]*)\b", stripped, flags=re.IGNORECASE))


def main() -> int:
    errors: list[str] = []
    ddl = read(DDL)
    seed = read(SEED)
    queries = read(QUERIES)
    explain = read(EXPLAIN)
    tables = table_names(ddl)
    indexes = index_names(ddl)
    constraints = constraint_names(ddl)

    if len(tables) < 25:
        errors.append(f"expected at least 25 tables in {DDL.relative_to(ROOT)}, found {len(tables)}")

    seed_refs = referenced_tables(seed)
    query_refs = referenced_tables(queries)
    explain_refs = referenced_tables(explain)
    for name in sorted((seed_refs | query_refs | explain_refs) - tables):
        errors.append(f"SQL references unknown table `{name}`")

    if ":changed_node_id" in queries:
        errors.append("examples/queries.sql must be runnable without the old :changed_node_id placeholder")
    if "explain (analyze, buffers" not in explain.lower():
        errors.append("examples/explain.sql must capture EXPLAIN (ANALYZE, BUFFERS) plans")

    missing_indexes = sorted(EXPECTED_INDEXES - indexes)
    if missing_indexes:
        errors.append(f"missing expected optimizer indexes: {missing_indexes}")
    missing_constraints = sorted(EXPECTED_CONSTRAINTS - constraints)
    if missing_constraints:
        errors.append(f"missing expected SQL constraints: {missing_constraints}")

    for path, sql in [(DDL, ddl), (SEED, seed), (QUERIES, queries), (EXPLAIN, explain)]:
        if sql.count("(") != sql.count(")"):
            errors.append(f"unbalanced parentheses in {path.relative_to(ROOT)}")
        stripped = "\n".join(line for line in sql.splitlines() if not line.strip().startswith("--")).strip()
        if stripped and not stripped.endswith(";"):
            errors.append(f"{path.relative_to(ROOT)} must end with a semicolon-terminated statement")

    if errors:
        print("SQL static check failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("SQL static check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
