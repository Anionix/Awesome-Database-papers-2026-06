-- Seed data for examples/queries.sql.
-- Load after docs/repo-db-schema.sql in an empty scratch database.

insert into repositories (repo_id, owner, name, default_branch)
values
  ('00000000-0000-0000-0000-000000000001', 'Anionix', 'Awesome-Database-papers-2026-06', 'main');

insert into files (file_id, repo_id, first_seen_at)
values
  ('00000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000001', '2026-06-29T08:34:00Z'),
  ('00000000-0000-0000-0000-000000000102', '00000000-0000-0000-0000-000000000001', '2026-06-29T08:34:00Z');

insert into file_versions (version_id, file_id, commit_sha, sha256, byte_size, language)
values
  ('00000000-0000-0000-0000-000000000201', '00000000-0000-0000-0000-000000000101', '23b81dee0619862ffb8bf5f23e0862cfa81f6e9f', 'sha256-readme', 11906, 'Markdown'),
  ('00000000-0000-0000-0000-000000000202', '00000000-0000-0000-0000-000000000102', '23b81dee0619862ffb8bf5f23e0862cfa81f6e9f', 'sha256-catalog', 42000, 'JSON');

insert into path_history (path_history_id, file_id, path, valid_from)
values
  ('00000000-0000-0000-0000-000000000301', '00000000-0000-0000-0000-000000000101', 'README.md', '2026-06-29T08:34:00Z'),
  ('00000000-0000-0000-0000-000000000302', '00000000-0000-0000-0000-000000000102', 'data/selected_papers.json', '2026-06-29T08:34:00Z');

insert into repo_nodes (node_id, repo_id, node_type, stable_key, display_name, file_id, version_id)
values
  ('00000000-0000-0000-0000-000000000401', '00000000-0000-0000-0000-000000000001', 'file', 'README.md', 'README.md', '00000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000201'),
  ('00000000-0000-0000-0000-000000000402', '00000000-0000-0000-0000-000000000001', 'schema', 'data/selected_papers.json', 'selected_papers.json', '00000000-0000-0000-0000-000000000102', '00000000-0000-0000-0000-000000000202'),
  ('00000000-0000-0000-0000-000000000403', '00000000-0000-0000-0000-000000000001', 'artifact', 'docs/curated-table.md', 'curated table', null, null),
  ('00000000-0000-0000-0000-000000000404', '00000000-0000-0000-0000-000000000001', 'query', 'examples/queries.sql#stale-artifacts', 'stale artifact query', null, null);

insert into graph_edges (edge_id, repo_id, src_node_id, dst_node_id, edge_type, source, confidence)
values
  ('00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000402', '00000000-0000-0000-0000-000000000403', 'generates', 'system', 1.0),
  ('00000000-0000-0000-0000-000000000502', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000401', '00000000-0000-0000-0000-000000000403', 'documents', 'user', 0.9);

insert into generated_artifacts (artifact_id, repo_id, artifact_path, artifact_type, generator_name, generator_version, output_sha256, stale_flag, created_at, refreshed_at)
values
  ('00000000-0000-0000-0000-000000000601', '00000000-0000-0000-0000-000000000001', 'docs/curated-table.md', 'markdown', 'scripts/generate_catalog.py', 'v1', 'sha256-curated-table', true, '2026-06-29T08:34:00Z', '2026-06-29T08:34:00Z');

insert into artifact_dependencies (artifact_id, source_node_id, source_version_id, dependency_role)
values
  ('00000000-0000-0000-0000-000000000601', '00000000-0000-0000-0000-000000000402', '00000000-0000-0000-0000-000000000202', 'canonical_catalog');

insert into refresh_plans (refresh_plan_id, artifact_id, strategy, plan_json)
values
  ('00000000-0000-0000-0000-000000000701', '00000000-0000-0000-0000-000000000601', 'full', '{"command":"make generate"}');

insert into refresh_runs (refresh_run_id, refresh_plan_id, artifact_id, status, output_sha256)
values
  ('00000000-0000-0000-0000-000000000702', '00000000-0000-0000-0000-000000000701', '00000000-0000-0000-0000-000000000601', 'succeeded', 'sha256-curated-table');

insert into ai_runs (ai_run_id, repo_id, node_id, task_type, model_name, prompt_sha256, input_sha256, output_sha256, confidence, cascade_stage, verified, latency_ms)
values
  ('00000000-0000-0000-0000-000000000801', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000402', 'classify', 'example-model', 'sha256-prompt', 'sha256-input', 'sha256-output', 0.72, 'small_model', false, 1800);

insert into model_costs (model_cost_id, ai_run_id, input_tokens, output_tokens, estimated_usd, memory_mb)
values
  ('00000000-0000-0000-0000-000000000802', '00000000-0000-0000-0000-000000000801', 1200, 400, 0.08, 512);

insert into verification_events (verification_id, ai_run_id, artifact_id, verification_type, status, score, notes)
values
  ('00000000-0000-0000-0000-000000000803', '00000000-0000-0000-0000-000000000801', '00000000-0000-0000-0000-000000000601', 'rule', 'needs_review', 0.72, 'Example unverified model output.');

insert into query_runs (query_run_id, repo_id, source_node_id, sql_sha256, query_text, engine, status, rows_read, rows_written, cpu_ms, latency_ms)
values
  ('00000000-0000-0000-0000-000000000901', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000404', 'sha256-query', 'select artifact_path from generated_artifacts where stale_flag', 'postgres', 'succeeded', 10, 0, 15, 23);

insert into explain_plans (explain_plan_id, query_run_id, plan_sha256, estimated_cost, estimated_rows, plan_json)
values
  ('00000000-0000-0000-0000-000000000902', '00000000-0000-0000-0000-000000000901', 'sha256-plan', 12.5, 1, '{"node":"Seq Scan"}');

insert into index_advice (advice_id, repo_id, proposed_by, ai_run_id, target_table, index_ddl, reason, status)
values
  ('00000000-0000-0000-0000-000000000903', '00000000-0000-0000-0000-000000000001', 'llm', '00000000-0000-0000-0000-000000000801', 'generated_artifacts', 'create index on generated_artifacts(stale_flag)', 'Speed up stale artifact checks.', 'rejected');

insert into benchmark_runs (benchmark_run_id, repo_id, benchmark_name, workload_sha256, baseline_label, candidate_label, status, metrics)
values
  ('00000000-0000-0000-0000-000000000904', '00000000-0000-0000-0000-000000000001', 'catalog-query-smoke', 'sha256-workload', 'baseline', 'candidate-index', 'succeeded', '{"latency_ms":23}');

insert into validation_results (validation_result_id, benchmark_run_id, advice_id, decision, reason)
values
  ('00000000-0000-0000-0000-000000000905', '00000000-0000-0000-0000-000000000904', '00000000-0000-0000-0000-000000000903', 'reject', 'Fixture keeps the advice rejected for example comparison.');

insert into vector_index_entries (vector_entry_id, repo_id, node_id, embedding_model, embedding_version, chunk_sha256, dimensions, vector_store)
values
  ('00000000-0000-0000-0000-000000001001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000401', 'example-embedding', 'v1', 'sha256-chunk', 384, 'pgvector');

insert into rag_eval_runs (rag_eval_run_id, repo_id, eval_name, dataset_sha256, chunker_version, embedding_model, reranker_model, generator_model, summary_metrics)
values
  ('00000000-0000-0000-0000-000000001101', '00000000-0000-0000-0000-000000000001', 'catalog-rag-smoke', 'sha256-dataset', 'v1', 'example-embedding', 'example-reranker', 'example-generator', '{"context_recall":0.8}');

insert into retrieval_metrics (retrieval_metric_id, rag_eval_run_id, query_id, context_recall, precision_at_k, latency_ms, memory_mb, update_cost_ms)
values
  ('00000000-0000-0000-0000-000000001102', '00000000-0000-0000-0000-000000001101', 'q1', 0.8, 0.75, 42, 256, 17);

insert into factuality_checks (factuality_check_id, rag_eval_run_id, query_id, answer_sha256, groundedness, factual_consistency, verifier, notes)
values
  ('00000000-0000-0000-0000-000000001103', '00000000-0000-0000-0000-000000001101', 'q1', 'sha256-answer', 0.85, 0.8, 'rule', 'Example groundedness check.');

analyze;
