# Databricks

## Theme

Generated artifacts as materialized views

## Adoptable idea

Treat generated files, summaries, diagrams, JSONL, TSV, and Mermaid outputs as materialized views over source repository state.

## Why it matters

A repository with generated artifacts needs freshness, dependency tracking, and refresh plans. Materialized-view thinking gives a clean model for rebuilds.

## Key papers / links

- [Enzyme: Incremental View Maintenance for Data Engineering](https://arxiv.org/abs/2603.27775) — primary / arXiv
- [Enzyme: Incremental View Maintenance With Spark Declarative Pipelines](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

`generated/*.tsv`, `*.jsonl`, `*.mmd`, and generated docs should have source hashes, refresh plans, stale flags, and incremental refresh metadata.

## First schema objects

- `generated_artifacts`
- `artifact_dependencies`
- `refresh_plans`
- `refresh_runs`
- `stale_flags`

## Do now

Record source file hashes for every generated artifact and mark artifacts stale when dependencies change.

## Do later

Add an incremental refresh planner that refreshes only affected artifacts rather than rebuilding everything.

## Caveat

Without lineage, generated docs silently drift from the source repository.

## Priority

P0
