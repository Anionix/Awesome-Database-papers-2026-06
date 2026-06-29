# Topic Map

This file is generated from `data/selected_papers.json`.

| Theme | Companies / papers | Repository database objects | Decision rule |
|---|---|---|---|
| Unified optimizer, vector, lineage, and SQL visibility | Alibaba: Learned Query Optimizer in Alibaba MaxCompute: Challenges, Analysis, and Solutions, LindormVector: A Distributed Vector Engine on a Cloud-Native Multi-Model NoSQL Database, SQLens: Continuous Code-to-SQL Visibility in the Wild, NebulaSQL: A Large-scale Feature Computation System for Online Recommendation | `query_runs`, `lineage_edges`, `vector_index_entries`, `code_to_sql_edges`, `optimizer_observations` | Connect execution, lineage, and retrieval. |
| Repository as production-scale graph and multimodal warehouse | ByteDance: ByteHouse: ByteDance’s Cloud-Native Data Warehouse for Real-Time Multimodal Data Analytics, ByteGraph-Dione: An Adaptive Dual-Format Graph Engine with Hotspot Awareness and Transaction Efficiency for Production-Scale Workloads, G2+D: A High Performance Distributed Graph Mining System | `repo_nodes`, `graph_edges`, `multimodal_chunks`, `execution_traces`, `embedding_runs` | Model repo knowledge as a typed graph. |
| Generated artifacts as materialized views | Databricks: Enzyme: Incremental View Maintenance for Data Engineering, Enzyme: Incremental View Maintenance With Spark Declarative Pipelines | `generated_artifacts`, `artifact_dependencies`, `refresh_plans`, `refresh_runs`, `stale_flags` | Generated files are materialized views. |
| Long-lived key-value / wide-column metadata design | Google: Twenty Years of Bigtable, Twenty Years of Bigtable | `files`, `file_versions`, `path_history`, `content_hashes`, `metadata_cells` | Paths change; stable IDs and hashes endure. |
| LLM recommendations must be validated by database tooling | Microsoft: Evaluating the Practical Effectiveness of LLM-Driven Index Tuning with Microsoft Database Tuning Advisor, Bitmap Filtering in the Fabric Data Warehouse, CoddSpeed: Hardware Accelerated Query Processing in Microsoft Fabric, ConDABench: Interactive Evaluation of Language Models for Data Analysis | `index_advice`, `explain_plans`, `benchmark_runs`, `workload_replays`, `validation_results` | Models propose; benchmarks decide. |
| Normalize documents, JSON, Markdown, and YAML into relational projections | Oracle: From JSON to Duality: Automated Application Migration from Document to Relational Databases, From JSON to Duality: Automated Application Migration from Document to Relational Databases | `docs`, `json_objects`, `schemas`, `relational_projection`, `document_projection_map` | Keep raw documents and relational projections. |
| AI operators inside the database optimizer | Snowflake: Streaming Model Cascades for Semantic SQL, Cortex AISQL: A Production SQL Engine for Unstructured Data | `ai_runs`, `model_costs`, `model_cascade_stages`, `semantic_operator_results`, `verification_events` | Store every AI operation as queryable data. |
| PostgreSQL-compatible horizontal scale | AWS: Aurora PostgreSQL Limitless Database: Building a Highly Scalable OLTP Database, Aurora PostgreSQL Limitless Database: Building a Highly Scalable OLTP Database | `router_rules`, `project_shards`, `replicas`, `global_transaction_log`, `shard_rebalancing_events` | Preserve relational compatibility before custom sharding. |
| End-to-end benchmarking for RAG and embeddings | IBM: RAGPerf: An End-to-End Benchmarking Framework for Retrieval-Augmented Generation Systems, Fabric-X: Scaling Hyperledger Fabric for Asset Exchange | `rag_eval_runs`, `retrieval_metrics`, `generation_metrics`, `rerank_metrics`, `factuality_checks` | Measure quality and system cost together. |
| Use graph databases when multi-hop queries become the bottleneck | Neo4j: RIOT: Replicated Independently-Ordered Transactions, Neo4j Research: RIOT, RIOT: Replicated Independently-Ordered Transactions | `graph_edges`, `graph_snapshots`, `neo4j_mirror_state`, `multi_hop_query_log` | Add graph DB after multi-hop workload evidence. |
| Distributed consensus for highly available metadata | Cockroach Labs: Scalable Leader Leases For Multi Consensus Groups in CockroachDB, Scalable Leader Leases For Multi Consensus Groups in CockroachDB | `metadata_ranges`, `leaseholders`, `consensus_groups`, `range_health_events`, `lease_transfer_events` | Use distributed SQL for HA metadata services. |
| Distributed design for heterogeneous multi-table workloads | Tencent: TDSQL-Boundless: A Distributed Database System for Large-scale Heterogeneous Multi-Table Workloads, TDSQL-Boundless: A Distributed Database System for Large-scale Heterogeneous Multi-Table Workloads | `project_shards`, `package_groups`, `heterogeneous_tables`, `workload_classes`, `cross_shard_queries` | Classify heterogeneous workloads early. |

## Practical grouping

### Must implement early

- Google-style stable file identity.
- Databricks-style generated artifact freshness.
- Snowflake/Microsoft-style AI logging and validation.
- Alibaba/ByteDance-style graph and lineage tables.
- Oracle-style document-to-relational projection.

### Implement after workload evidence

- Neo4j mirror for graph traversal.
- AWS-style router/shard layer.
- Cockroach-style consensus metadata ranges.
- Tencent-style heterogeneous distributed routing.

### Evaluate continuously

- IBM/RAGPerf-style RAG benchmark suite.
- Microsoft-style optimizer/benchmark gates for LLM proposals.
