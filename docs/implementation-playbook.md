# Implementation Playbook

This playbook turns the curated papers into a concrete repo/database management architecture.

## Runnable starter

The starter SQL is intentionally PostgreSQL-flavored and dependency-light.

```sh
make sql-check
```

Static SQL checks always run. To execute the schema, seed data, sample queries, and `EXPLAIN (ANALYZE, BUFFERS)` wrappers, point `DATABASE_URL` at an empty scratch PostgreSQL database before running `make sql-check`.

The DDL includes both starter tables and thin future-extension tables. Future-extension tables keep the playbook, topic map, and catalog object names aligned, but the build order below still recommends implementing identity, artifacts, AI validation, query lineage, and RAG evaluation before distributed metadata operations.

See `docs/database-optimizer-notes.md` for the baseline-first index and query review workflow.

## Stage 0 — Do not start with distributed systems

Start with a single PostgreSQL database and a simple ingestion pipeline. The first objective is correctness: stable IDs, content hashes, lineage, and reproducible generated artifacts. Distributed SQL, Neo4j, and shard routers are later steps.

## Stage 1 — Stable repository identity

Inspired by Google Bigtable's long-term operational lesson: metadata must survive years of evolution.

Create:

- `files`: logical file identity.
- `file_versions`: immutable content snapshots.
- `path_history`: path changes over time.
- `content_hashes`: sha256 and optional language/parser fingerprints.
- `repo_nodes`: a generic node table for files, symbols, docs, schemas, tests, proofs, and embeddings.

Rule: `path` is not the identity. `file_id` and `sha256` are the identity anchors.

## Stage 2 — Generated artifacts as materialized views

Inspired by Databricks Enzyme.

Generated artifacts include summaries, diagrams, JSONL exports, TSV indexes, Mermaid graphs, schema snapshots, and RAG chunks. Treat them as materialized views.

Create:

- `generated_artifacts`
- `artifact_dependencies`
- `refresh_plans`
- `refresh_runs`
- `stale_flags`

Rule: every generated artifact must answer: “Which source objects produced me, which code produced me, and am I stale?”

## Stage 3 — AI calls as database records

Inspired by Snowflake Semantic SQL/Cortex AISQL and Microsoft DTA validation.

Create:

- `ai_runs`
- `model_costs`
- `model_cascade_stages`
- `semantic_operator_results`
- `verification_events`
- `index_advice`
- `explain_plans`
- `benchmark_runs`
- `validation_results`

Rule: LLM output is never directly trusted. It is proposed, logged, costed, benchmarked, and verified.

## Stage 4 — Query, lineage, vector, and graph fabric

Inspired by Alibaba MaxCompute, LindormVector, SQLens, ByteHouse, ByteGraph-Dione, and Neo4j RIOT.

Create:

- `query_runs`
- `lineage_edges`
- `code_to_sql_edges`
- `vector_index_entries`
- `graph_edges`
- `graph_snapshots`
- `multi_hop_query_log`

Rule: keep graph edges in PostgreSQL first. Mirror to Neo4j only after multi-hop graph workloads dominate.

## Stage 5 — RAG evaluation discipline

Inspired by RAGPerf.

Create:

- `rag_eval_runs`
- `retrieval_metrics`
- `rerank_metrics`
- `generation_metrics`
- `factuality_checks`

Evaluate:

- context recall
- answer groundedness
- factual consistency
- latency
- memory
- index update cost
- retrieval/update ratio

Rule: a better answer is not better if the system becomes too slow or too expensive to update.

## Stage 6 — Scale-out only with evidence

Inspired by AWS Aurora Limitless, CockroachDB leader leases, and Tencent TDSQL-Boundless.

Add later:

- `router_rules`
- `project_shards`
- `replicas`
- `global_transaction_log`
- `metadata_ranges`
- `leaseholders`
- `consensus_groups`
- `workload_classes`

Scale triggers:

- single-node PostgreSQL cannot meet latency or throughput requirements;
- metadata is shared by many teams/services;
- cross-project workloads are heterogeneous;
- high availability is required;
- maintenance windows become unacceptable.

Rule: do not confuse schema complexity with distributed-system need. Normalize and benchmark first.

## Recommended build order

1. `files`, `file_versions`, `path_history`
2. `repo_nodes`, `graph_edges`
3. `generated_artifacts`, `artifact_dependencies`, `refresh_runs`
4. `ai_runs`, `model_costs`, `verification_events`
5. `query_runs`, `lineage_edges`, `code_to_sql_edges`
6. `vector_index_entries`, `rag_eval_runs`
7. `project_shards`, `metadata_ranges`, `consensus_groups` only if needed

## Example execution path

1. Load `docs/repo-db-schema.sql` into a scratch PostgreSQL database.
2. Load `examples/seed.sql`.
3. Run `examples/queries.sql`.
4. Run `examples/explain.sql` and save the plan output before changing indexes or query shape.
5. Replace the seed rows with real repository ingestion once identity, artifact, AI, query, graph, and RAG records are available.
