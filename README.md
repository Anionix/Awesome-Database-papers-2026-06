# Awesome Database Papers 2026-06

A curated, GitHub-ready reading list and implementation playbook for database-system papers around SIGMOD/PODS 2026, focused on **how to turn research ideas into a practical repository metadata database**.

This repository is intentionally selective. It does not try to list every accepted paper. It selects papers and company systems that map cleanly to a repo/database management architecture: AI-in-DB, optimizer validation, generated artifacts as materialized views, long-lived metadata identity, graph lineage, vector/RAG evaluation, and distributed metadata storage.

> Scope note: this repository stores links, summaries, and implementation ideas. It does **not** redistribute paper PDFs.

## Fast takeaway

Build the repository database in this order:

1. **Stable metadata foundation**: files, versions, paths, content hashes, symbols, docs, schemas.
2. **Generated artifacts as materialized views**: every generated `*.jsonl`, `*.tsv`, `*.mmd`, summary, and report has lineage and freshness state.
3. **AI operations with validation**: every LLM/AI call has cost, confidence, cascade stage, and verification status.
4. **Graph + lineage + vector layer**: code, docs, schemas, tests, proofs, and embeddings become typed nodes and edges.
5. **Benchmark before trusting RAG**: measure recall, latency, memory, update cost, and factual consistency together.
6. **Scale out only when needed**: start with PostgreSQL; add routers, shards, replicas, Neo4j, or distributed SQL only when workload evidence justifies it.

## Curated company-to-implementation map

| Company | Adoptable idea | Key papers / source links | Repo / DB translation |
|---|---|---|---|
| **Snowflake** | Treat LLM/AI calls as first-class database operators with measurable cost, quality, confidence, and fallback behavior. | [Streaming Model Cascades for Semantic SQL](https://arxiv.org/abs/2604.00660)<br>[Cortex AISQL: A Production SQL Engine for Unstructured Data](https://2026.sigmod.org/sigmod_industry_papers.shtml) | `ai_runs`, `model_cost`, `confidence`, `cascade_stage`, and `verified` should be stored alongside query and artifact metadata. |
| **Microsoft** | Use LLMs for proposal generation, but rely on EXPLAIN plans, replay, benchmarks, and optimizer tooling for acceptance. | [Evaluating the Practical Effectiveness of LLM-Driven Index Tuning with Microsoft Database Tuning Advisor](https://arxiv.org/abs/2603.09181)<br>[Bitmap Filtering in the Fabric Data Warehouse](https://2026.sigmod.org/sigmod_industry_papers.shtml)<br>[CoddSpeed: Hardware Accelerated Query Processing in Microsoft Fabric](https://2026.sigmod.org/sigmod_industry_papers.shtml) | LLM-generated index/schema advice must pass `EXPLAIN`, benchmark runs, workload replay, and rollback checks before being merged. |
| **Databricks** | Treat generated files, summaries, diagrams, JSONL, TSV, and Mermaid outputs as materialized views over source repository state. | [Enzyme: Incremental View Maintenance for Data Engineering](https://arxiv.org/abs/2603.27775)<br>[Enzyme: Incremental View Maintenance With Spark Declarative Pipelines](https://2026.sigmod.org/sigmod_industry_papers.shtml) | `generated/*.tsv`, `*.jsonl`, `*.mmd`, and generated docs should have source hashes, refresh plans, stale flags, and incremental refresh metadata. |
| **AWS** | Start with normal PostgreSQL semantics, then add router, shard, replica, and distributed transaction concepts only when scale demands it. | [Aurora PostgreSQL Limitless Database: Building a Highly Scalable OLTP Database](https://www.amazon.science/publications/aurora-postgresql-limitless-database-building-a-highly-scalable-oltp-database)<br>[Aurora PostgreSQL Limitless Database: Building a Highly Scalable OLTP Database](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Begin with single PostgreSQL. When repositories or organizations grow, introduce logical routers, project shards, replicas, and distributed transaction logs. |
| **Google** | Optimize metadata identity for decades: stable keys, versioned paths, immutable content hashes, and forward-compatible columns. | [Twenty Years of Bigtable](https://research.google/pubs/twenty-years-of-bigtable/)<br>[Twenty Years of Bigtable](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Use `file_id`, `path`, `sha256`, `version`, `valid_from`, `valid_to`, and `path_history` so metadata remains stable across renames and rebuilds. |
| **Alibaba** | Connect query execution, vector search, lineage, and code-to-SQL visibility into one metadata fabric. | [Learned Query Optimizer in Alibaba MaxCompute: Challenges, Analysis, and Solutions](https://arxiv.org/abs/2602.07336)<br>[LindormVector: A Distributed Vector Engine on a Cloud-Native Multi-Model NoSQL Database](https://2026.sigmod.org/sigmod_industry_papers.shtml)<br>[SQLens: Continuous Code-to-SQL Visibility in the Wild](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Store `graph_edges`, `lineage`, `query_runs`, `vector_index`, and `code_to_sql_edges` as connected concepts. |
| **ByteDance** | Represent code, docs, schemas, tests, proofs, embeddings, and execution traces as graph-connected multimodal objects. | [ByteHouse: ByteDance’s Cloud-Native Data Warehouse for Real-Time Multimodal Data Analytics](https://arxiv.org/abs/2602.08226)<br>[ByteGraph-Dione: An Adaptive Dual-Format Graph Engine with Hotspot Awareness and Transaction Efficiency for Production-Scale Workloads](https://2026.sigmod.org/sigmod_industry_papers.shtml)<br>[G2+D: A High Performance Distributed Graph Mining System](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Model `file`, `symbol`, `doc`, `schema`, `test`, `proof`, and `embedding` as graph nodes with typed edges. |
| **IBM** | Measure RAG as a whole system: embedding, indexing, retrieval, reranking, generation, latency, memory, update cost, and factual consistency. | [RAGPerf: An End-to-End Benchmarking Framework for Retrieval-Augmented Generation Systems](https://arxiv.org/abs/2603.10765)<br>[Fabric-X: Scaling Hyperledger Fabric for Asset Exchange](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Persist `rag_eval_runs`, `context_recall`, `latency`, `memory`, `update_cost`, `answer_groundedness`, and `factual_consistency`. |
| **Oracle** | Keep developer-friendly document formats, but project them into relational tables for querying, constraints, migration, and governance. | [From JSON to Duality: Automated Application Migration from Document to Relational Databases](https://dl.acm.org/doi/10.1145/3788853.3803096)<br>[From JSON to Duality: Automated Application Migration from Document to Relational Databases](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Normalize `md`, `json`, and `yaml` into `schemas/*.schema.json`, relational tables, and dual document/relational views. |
| **Neo4j** | Start with `graph_edges` in PostgreSQL, then mirror to Neo4j when multi-hop traversal and graph algorithms dominate workload cost. | [RIOT: Replicated Independently-Ordered Transactions](https://dl.acm.org/doi/10.1145/3788853.3803094)<br>[Neo4j Research: RIOT](https://neo4j.com/research/)<br>[RIOT: Replicated Independently-Ordered Transactions](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Use PostgreSQL `graph_edges` first. Add a Neo4j mirror only after multi-hop queries, path ranking, or graph algorithms justify it. |
| **Cockroach Labs** | Leader leases and range-level consensus matter once repository metadata becomes a shared, high-availability service. | [Scalable Leader Leases For Multi Consensus Groups in CockroachDB](https://www.cockroachlabs.com/blog/distributed-database-leader-leases/)<br>[Scalable Leader Leases For Multi Consensus Groups in CockroachDB](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Use `metadata_ranges`, `leaseholders`, `consensus_groups`, and range-health observations when evolving toward distributed metadata storage. |
| **Tencent** | Plan for multiple languages, package managers, schema styles, artifact types, and workload classes in large monorepos. | [TDSQL-Boundless: A Distributed Database System for Large-scale Heterogeneous Multi-Table Workloads](https://dl.acm.org/doi/abs/10.1145/3788853.3803090)<br>[TDSQL-Boundless: A Distributed Database System for Large-scale Heterogeneous Multi-Table Workloads](https://2026.sigmod.org/sigmod_industry_papers.shtml) | Use `project_shards`, `package_groups`, `heterogeneous_tables`, and workload-class routing for multi-language monorepo metadata. |

## Reading path

### 1. AI inside the database
Start with Snowflake, Microsoft, and Alibaba. They give the cleanest guidance for integrating model calls, learned optimization, and validation into database workflows. The repo-level rule is simple: **AI output is data, not magic**. Store its cost, confidence, input hash, output hash, and verification state.

### 2. Generated artifacts as database views
Read Databricks Enzyme next. A generated repository artifact should behave like a materialized view: it has dependencies, freshness, a refresh plan, and a rebuild history.

### 3. Long-lived metadata
Read Google Bigtable and AWS Aurora Limitless together. Bigtable argues for stable identity over long time spans; Aurora shows how relational compatibility can coexist with horizontal scale. For a GitHub-scale repository metadata DB, use stable IDs and PostgreSQL first, then scale out.

### 4. Graph, vector, and lineage
Read Alibaba, ByteDance, and Neo4j as a cluster. Keep a relational `graph_edges` table first. Add specialized graph/vector infrastructure only when query patterns demand it.

### 5. RAG as a measured system
Use IBM/RAGPerf as the evaluation discipline. Do not evaluate repository RAG only by retrieval recall. Add latency, memory, update cost, and factual consistency.

### 6. Distributed metadata operations
Read Cockroach Labs and Tencent last. Their ideas matter when metadata is a critical, multi-tenant service with many concurrent readers/writers and heterogeneous workloads.

## Repository contents

- [`docs/curated-table.md`](docs/curated-table.md): detailed table with paper links, mapping, and caveats.
- [`docs/implementation-playbook.md`](docs/implementation-playbook.md): step-by-step architecture plan.
- [`docs/schema-design.md`](docs/schema-design.md): conceptual schema and entity definitions.
- [`docs/repo-db-schema.sql`](docs/repo-db-schema.sql): PostgreSQL-flavored starter DDL.
- [`docs/topic-map.md`](docs/topic-map.md): map from themes to papers and database objects.
- [`docs/architecture.mmd`](docs/architecture.mmd): Mermaid architecture diagram.
- [`docs/paper-notes/`](docs/paper-notes/): one note per company.
- [`data/selected_papers.csv`](data/selected_papers.csv): machine-readable CSV.
- [`data/selected_papers.json`](data/selected_papers.json): machine-readable JSON.
- [`examples/`](examples/): small JSONL/TSV examples for metadata, AI runs, and lineage edges.

## Minimal schema mental model

```text
files / file_versions / path_history
  -> symbols / docs / schemas / generated_artifacts
  -> graph_edges / lineage_edges / query_runs
  -> ai_runs / model_costs / verification_events
  -> vector_index_entries / rag_eval_runs
  -> project_shards / consensus_groups / replicas (later)
```

## Selection criteria

A paper was selected if it answered at least one implementation question:

- How should AI/LLM calls be represented in a database system?
- How should generated artifacts stay fresh and reproducible?
- How should repository metadata survive path changes and long-term evolution?
- How should graph, vector, and lineage metadata be connected?
- How should RAG be benchmarked as a full system?
- When should a metadata database become distributed?

## Maintainer note

Use this as a seed repository. Add new papers only when they change a concrete design decision, table, benchmark, or operational rule.
