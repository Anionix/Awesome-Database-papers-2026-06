# Topic Map

| Theme | Companies / papers | Repository database objects | Decision rule |
|---|---|---|---|
| AI operators in SQL | Snowflake Semantic SQL, Cortex AISQL | `ai_runs`, `model_costs`, `semantic_operator_results` | Store every AI operation as queryable data. |
| LLM proposal validation | Microsoft DTA index tuning | `index_advice`, `explain_plans`, `benchmark_runs`, `validation_results` | Models propose; benchmarks decide. |
| Materialized generated artifacts | Databricks Enzyme | `generated_artifacts`, `artifact_dependencies`, `refresh_runs` | Generated files are materialized views. |
| PostgreSQL-compatible scale-out | AWS Aurora Limitless | `router_rules`, `project_shards`, `replicas` | Preserve relational compatibility before custom sharding. |
| Long-term metadata identity | Google Bigtable | `files`, `file_versions`, `path_history`, `sha256` | Paths change; stable IDs and hashes endure. |
| Learned optimizer + lineage + vector | Alibaba MaxCompute, LindormVector, SQLens | `query_runs`, `lineage_edges`, `vector_index_entries`, `code_to_sql_edges` | Connect execution, lineage, and retrieval. |
| Multimodal warehouse + graph | ByteDance ByteHouse, ByteGraph-Dione, G2+D | `repo_nodes`, `graph_edges`, `multimodal_chunks`, `execution_traces` | Model repo knowledge as a typed graph. |
| RAG benchmarking | IBM RAGPerf | `rag_eval_runs`, `retrieval_metrics`, `factuality_checks` | Measure quality and system cost together. |
| Document-to-relational migration | Oracle JSON to Duality | `docs`, `json_objects`, `schemas`, `relational_projection` | Keep raw documents and relational projections. |
| Graph transactions | Neo4j RIOT | `graph_edges`, `neo4j_mirror_state`, `multi_hop_query_log` | Add graph DB after multi-hop workload evidence. |
| Distributed consensus | Cockroach Leader Leases | `metadata_ranges`, `leaseholders`, `consensus_groups` | Use distributed SQL for HA metadata services. |
| Heterogeneous distributed workloads | Tencent TDSQL-Boundless | `project_shards`, `package_groups`, `workload_classes` | Classify heterogeneous workloads early. |

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
