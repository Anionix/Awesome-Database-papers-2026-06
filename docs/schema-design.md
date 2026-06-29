# Schema Design

This document explains the conceptual database schema behind the curated paper mapping.

## Core principles

1. **Stable identity beats path identity**: paths move; hashes and stable IDs endure.
2. **Generated artifacts are materialized views**: they need dependency tracking and refresh state.
3. **AI outputs are data**: store prompts, model names, costs, confidence, latency, and verification results.
4. **Graph edges start relational**: use `graph_edges` in PostgreSQL before adding a graph DB.
5. **RAG must be benchmarked end to end**: retrieval metrics alone are insufficient.
6. **Distribution is a late optimization**: add shards and consensus after the single-node model is correct.

## Entity groups

`docs/repo-db-schema.sql` defines the entity groups below. Some tables are thin future-extension tables so that catalog object names, documentation, and SQL stay synchronized without implying that distributed systems or specialized graph/vector infrastructure should be adopted early.

### Repository identity

- `files`: one logical file across renames.
- `file_versions`: immutable content snapshots.
- `path_history`: path validity intervals.
- `content_hashes`: sha256 and optional parser-derived hashes.

### Repository graph

- `repo_nodes`: common node table for files, symbols, docs, tests, schemas, generated artifacts, and embeddings.
- `graph_edges`: typed relationships such as `imports`, `defines`, `tests`, `documents`, `generates`, `depends_on`, `embeds`, and `verifies`.
- `graph_snapshots`: versioned graph views for reproducible analysis.

### Generated artifacts

- `generated_artifacts`: generated files or records.
- `artifact_dependencies`: source nodes that produced an artifact.
- `refresh_plans`: how an artifact should be updated.
- `refresh_runs`: actual refresh history.

### AI and semantic operators

- `ai_runs`: one model invocation or semantic operation.
- `model_costs`: token, latency, and price estimates.
- `model_cascade_stages`: fast model, oracle model, cache, human review, or fallback.
- `verification_events`: benchmark, human, rule, or replay validation.

### Query and optimization

- `query_runs`: executed SQL or generated SQL.
- `explain_plans`: optimizer plans and cost estimates.
- `index_advice`: proposed indexes or schema changes.
- `benchmark_runs`: reproducible workload tests.
- `validation_results`: accepted/rejected decisions and reasons.

### RAG and vector search

- `vector_index_entries`: embeddings linked to repository nodes and model versions.
- `rag_eval_runs`: evaluation suite execution.
- `retrieval_metrics`, `rerank_metrics`, `generation_metrics`, `factuality_checks`: detailed benchmark outcomes.

### Scale-out metadata

- `project_shards`: logical shard boundaries.
- `router_rules`: routing policy.
- `metadata_ranges`: Cockroach-like metadata ranges.
- `leaseholders`: current read/write authority for ranges.
- `consensus_groups`: replicated groups and health.

## Starter vs future-extension tables

Starter tables are the first implementation target: `repositories`, file identity, `repo_nodes`, `graph_edges`, generated artifacts, AI runs, query/benchmark validation, vector index entries, and RAG evaluation records.

Future-extension tables are included to keep the DDL executable and names traceable: router rules, replicas, transaction logs, range health, package groups, heterogeneous workloads, Neo4j mirror state, and multi-hop query logs. Treat them as schema placeholders until workload evidence requires them.

## Recommended IDs

Use UUIDs for logical entities and content hashes for immutable content.

```text
file_id     = stable UUID for logical file
version_id  = stable UUID for a content snapshot
node_id     = stable UUID for a graph node
artifact_id = stable UUID for a generated artifact
run_id      = stable UUID for a model/query/benchmark run
sha256      = immutable content identity
```

## Minimal edge types

```text
defines       file -> symbol
imports       file -> file or symbol
calls         symbol -> symbol
documents     doc -> symbol/schema/file
tests         test -> symbol/file
generates     source -> generated_artifact
depends_on    artifact -> source
embeds        embedding -> chunk/node
queries       code -> sql/query_run
verifies      benchmark/test -> artifact or model output
```
