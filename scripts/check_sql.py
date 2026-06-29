#!/usr/bin/env python3
"""Static SQL sanity checks for schema, seed data, and example queries."""

from __future__ import annotations

import pathlib
import sys

from sql_corpus import constraint_names, index_names, referenced_tables, table_names

ROOT = pathlib.Path(__file__).resolve().parents[1]
DDL = ROOT / "docs" / "repo-db-schema.sql"
SEED = ROOT / "examples" / "seed.sql"
QUERIES = ROOT / "examples" / "queries.sql"
EXPLAIN = ROOT / "examples" / "explain.sql"

# LLM contract: these names pin review-driven optimizer and lineage guarantees.
# If the DDL changes, update the DDL and this list together.
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
    # Seed, query, and EXPLAIN examples are part of the executable playbook.
    # Every table they mention must exist in the DDL.
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
