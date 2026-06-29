# Database Optimizer Notes

This repository includes starter PostgreSQL DDL and sample queries. Optimization changes should follow the same discipline used for production databases: capture a baseline, change one thing, and validate the result.

## Baseline first

Run examples against a scratch database before changing query shape or indexes:

```sh
DATABASE_URL=postgres://localhost/awesome_db_papers_scratch make sql-check
```

For manual analysis, load the schema and seed data, then run:

```sh
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f docs/repo-db-schema.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f examples/seed.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f examples/explain.sql
```

Save the `EXPLAIN (ANALYZE, BUFFERS)` output before and after each optimization.

## Index strategy

The DDL includes indexes for the current sample query patterns:

- stale artifact lookups use `generated_artifacts_stale_idx` plus `artifact_dependencies_source_idx`;
- graph neighborhood lookups use `graph_edges_src_idx` and `graph_edges_dst_idx`;
- unverified high-cost AI output lookups use `ai_runs_unverified_idx` and `model_costs_ai_run_idx`;
- RAG quality/cost joins use `retrieval_metrics_eval_query_idx` and `factuality_checks_eval_query_idx`;
- validation and benchmark review use status/decision indexes on advice, benchmark, and validation tables.

These indexes are intended for an empty starter database. In an existing database, create comparable indexes with `CREATE INDEX CONCURRENTLY` and watch write amplification.

## Query review checklist

- Use `EXPLAIN (ANALYZE, BUFFERS)` for real before/after evidence.
- Check row-estimate quality; run `ANALYZE` after bulk seed or ingestion loads.
- Prefer indexes that match actual joins, filters, and ordering.
- Avoid adding indexes that only make tiny fixture data look faster.
- Document rejected index advice in `index_advice` and `validation_results`.
