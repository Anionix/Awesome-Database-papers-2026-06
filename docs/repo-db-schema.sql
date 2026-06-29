-- Awesome Database Papers 2026-06
-- PostgreSQL-flavored starter DDL for a repository metadata database.
-- This schema is conceptual. Adapt data types, indexes, and partitioning for production.
-- Indexes here are safe for an empty scratch database. In an existing production
-- database, create comparable indexes with CREATE INDEX CONCURRENTLY and measure
-- EXPLAIN (ANALYZE, BUFFERS) before and after each change.

create extension if not exists pgcrypto;

-- -----------------------------
-- Repository identity
-- -----------------------------

create table repositories (
  repo_id uuid primary key default gen_random_uuid(),
  owner text not null,
  name text not null,
  default_branch text,
  created_at timestamptz not null default now(),
  unique (owner, name)
);

create table files (
  file_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  first_seen_at timestamptz not null default now(),
  logical_status text not null default 'active',
  unique (repo_id, file_id)
);

create table file_versions (
  version_id uuid primary key default gen_random_uuid(),
  file_id uuid not null references files(file_id),
  commit_sha text,
  sha256 text not null,
  byte_size bigint,
  language text,
  parser_fingerprint text,
  captured_at timestamptz not null default now(),
  unique (file_id, sha256)
);

create table content_hashes (
  content_hash_id uuid primary key default gen_random_uuid(),
  version_id uuid not null references file_versions(version_id),
  hash_type text not null, -- sha256, parser, normalized_ast, embedding_chunk
  hash_value text not null,
  created_at timestamptz not null default now(),
  unique (version_id, hash_type)
);

create table path_history (
  path_history_id uuid primary key default gen_random_uuid(),
  file_id uuid not null references files(file_id),
  path text not null,
  valid_from timestamptz not null,
  valid_to timestamptz,
  unique (file_id, path, valid_from)
);

create table metadata_cells (
  metadata_cell_id uuid primary key default gen_random_uuid(),
  file_id uuid not null references files(file_id),
  cell_family text not null,
  qualifier text not null,
  value_json jsonb not null default '{}'::jsonb,
  valid_from timestamptz not null default now(),
  valid_to timestamptz,
  unique (file_id, cell_family, qualifier, valid_from)
);

-- -----------------------------
-- Generic repository graph
-- -----------------------------

create table repo_nodes (
  node_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  node_type text not null, -- file, symbol, doc, schema, test, proof, chunk, embedding, artifact
  stable_key text not null,
  display_name text,
  file_id uuid references files(file_id),
  version_id uuid references file_versions(version_id),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (repo_id, node_type, stable_key)
);

create table docs (
  doc_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  node_id uuid references repo_nodes(node_id),
  path text not null,
  title text,
  raw_sha256 text,
  parsed_at timestamptz not null default now(),
  unique (repo_id, path)
);

create table json_objects (
  json_object_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  node_id uuid references repo_nodes(node_id),
  source_path text not null,
  json_pointer text not null,
  value_json jsonb not null,
  created_at timestamptz not null default now(),
  unique (repo_id, source_path, json_pointer)
);

create table schemas (
  schema_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  node_id uuid references repo_nodes(node_id),
  schema_name text not null,
  schema_path text,
  schema_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (repo_id, schema_name)
);

create table relational_projection (
  projection_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  source_node_id uuid references repo_nodes(node_id),
  target_table text not null,
  projection_sql text,
  created_at timestamptz not null default now()
);

create table document_projection_map (
  document_projection_map_id uuid primary key default gen_random_uuid(),
  doc_id uuid references docs(doc_id),
  projection_id uuid references relational_projection(projection_id),
  source_pointer text,
  target_column text,
  transform text,
  unique (doc_id, projection_id, source_pointer, target_column)
);

create table multimodal_chunks (
  chunk_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  node_id uuid references repo_nodes(node_id),
  chunk_type text not null, -- markdown, code, schema, trace, table, image_ref
  chunk_sha256 text not null,
  content_ref text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (repo_id, chunk_sha256)
);

create table graph_edges (
  edge_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  src_node_id uuid not null references repo_nodes(node_id),
  dst_node_id uuid not null references repo_nodes(node_id),
  edge_type text not null, -- imports, calls, defines, tests, documents, generates, depends_on, embeds
  source text not null default 'parser', -- parser, llm, test, user, system
  confidence numeric(5,4),
  valid_from timestamptz not null default now(),
  valid_to timestamptz,
  evidence jsonb not null default '{}'::jsonb
);

create index graph_edges_src_idx on graph_edges(src_node_id, edge_type);
create index graph_edges_dst_idx on graph_edges(dst_node_id, edge_type);
create index graph_edges_repo_type_idx on graph_edges(repo_id, edge_type, valid_from);

create table graph_snapshots (
  graph_snapshot_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  snapshot_label text not null,
  source_commit_sha text,
  node_count bigint,
  edge_count bigint,
  created_at timestamptz not null default now(),
  unique (repo_id, snapshot_label)
);

create table lineage_edges (
  lineage_edge_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  src_node_id uuid not null references repo_nodes(node_id),
  dst_node_id uuid not null references repo_nodes(node_id),
  lineage_type text not null, -- derives, refreshes, validates, materializes
  source text not null default 'system',
  confidence numeric(5,4),
  created_at timestamptz not null default now()
);

create index lineage_edges_src_idx on lineage_edges(src_node_id, lineage_type);
create index lineage_edges_dst_idx on lineage_edges(dst_node_id, lineage_type);

create table code_to_sql_edges (
  code_to_sql_edge_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  source_node_id uuid not null references repo_nodes(node_id),
  query_run_id uuid,
  sql_sha256 text not null,
  extraction_source text not null default 'parser',
  confidence numeric(5,4),
  created_at timestamptz not null default now()
);

create index code_to_sql_edges_source_idx on code_to_sql_edges(source_node_id, sql_sha256);

create table execution_traces (
  execution_trace_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  node_id uuid references repo_nodes(node_id),
  trace_type text not null,
  trace_sha256 text,
  summary jsonb not null default '{}'::jsonb,
  captured_at timestamptz not null default now()
);

create index execution_traces_node_type_idx on execution_traces(node_id, trace_type, captured_at);

create table embedding_runs (
  embedding_run_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  embedding_model text not null,
  embedding_version text,
  chunker_version text,
  status text not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  metrics jsonb not null default '{}'::jsonb
);

-- -----------------------------
-- Generated artifacts as materialized views
-- -----------------------------

create table generated_artifacts (
  artifact_id uuid primary key default gen_random_uuid(),
  repo_id uuid not null references repositories(repo_id),
  artifact_path text not null,
  artifact_type text not null, -- jsonl, tsv, mermaid, markdown, report, schema_snapshot
  generator_name text not null,
  generator_version text,
  output_sha256 text,
  stale_flag boolean not null default false,
  created_at timestamptz not null default now(),
  refreshed_at timestamptz,
  unique (repo_id, artifact_path)
);

create index generated_artifacts_stale_idx
  on generated_artifacts(repo_id, artifact_type, artifact_path)
  where stale_flag = true;

create table stale_flags (
  stale_flag_id uuid primary key default gen_random_uuid(),
  artifact_id uuid not null references generated_artifacts(artifact_id),
  reason text not null,
  detected_at timestamptz not null default now(),
  resolved_at timestamptz,
  evidence jsonb not null default '{}'::jsonb
);

create index stale_flags_open_idx on stale_flags(artifact_id, detected_at) where resolved_at is null;

create table artifact_dependencies (
  artifact_id uuid not null references generated_artifacts(artifact_id),
  source_node_id uuid not null references repo_nodes(node_id),
  source_version_id uuid references file_versions(version_id),
  dependency_role text not null default 'source',
  primary key (artifact_id, source_node_id, dependency_role)
);

create index artifact_dependencies_source_idx on artifact_dependencies(source_node_id, artifact_id);

create table refresh_plans (
  refresh_plan_id uuid primary key default gen_random_uuid(),
  artifact_id uuid not null references generated_artifacts(artifact_id),
  strategy text not null, -- full, incremental, cache_only, manual
  plan_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table refresh_runs (
  refresh_run_id uuid primary key default gen_random_uuid(),
  refresh_plan_id uuid references refresh_plans(refresh_plan_id),
  artifact_id uuid not null references generated_artifacts(artifact_id),
  status text not null, -- succeeded, failed, skipped
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  input_summary jsonb not null default '{}'::jsonb,
  output_sha256 text,
  error text
);

create index refresh_runs_artifact_status_idx on refresh_runs(artifact_id, status, started_at desc);

-- -----------------------------
-- AI / semantic operator metadata
-- -----------------------------

create table ai_runs (
  ai_run_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  node_id uuid references repo_nodes(node_id),
  task_type text not null, -- summarize, classify, semantic_filter, index_advice, code_to_sql, rag_answer
  model_name text not null,
  model_version text,
  prompt_sha256 text,
  input_sha256 text,
  output_sha256 text,
  confidence numeric(5,4),
  cascade_stage text, -- cache, small_model, oracle_model, human_review, fallback
  verified boolean not null default false,
  latency_ms integer,
  created_at timestamptz not null default now()
);

create index ai_runs_unverified_idx
  on ai_runs(repo_id, created_at desc)
  include (task_type, model_name, cascade_stage, confidence, latency_ms)
  where verified = false;

create table model_cascade_stages (
  model_cascade_stage_id uuid primary key default gen_random_uuid(),
  ai_run_id uuid not null references ai_runs(ai_run_id),
  stage_name text not null, -- cache, small_model, oracle_model, human_review, fallback
  model_name text,
  status text not null,
  confidence numeric(5,4),
  latency_ms integer,
  created_at timestamptz not null default now()
);

create index model_cascade_stages_run_idx on model_cascade_stages(ai_run_id, stage_name, created_at);

create table semantic_operator_results (
  semantic_operator_result_id uuid primary key default gen_random_uuid(),
  ai_run_id uuid not null references ai_runs(ai_run_id),
  operator_name text not null,
  input_ref text,
  output_ref text,
  result_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index semantic_operator_results_run_idx on semantic_operator_results(ai_run_id, operator_name);

create table model_costs (
  model_cost_id uuid primary key default gen_random_uuid(),
  ai_run_id uuid not null references ai_runs(ai_run_id),
  input_tokens integer,
  output_tokens integer,
  estimated_usd numeric(12,6),
  memory_mb numeric(12,2),
  gpu_ms numeric(14,2),
  recorded_at timestamptz not null default now()
);

create index model_costs_ai_run_idx on model_costs(ai_run_id, estimated_usd desc, recorded_at desc);

create table verification_events (
  verification_id uuid primary key default gen_random_uuid(),
  ai_run_id uuid references ai_runs(ai_run_id),
  artifact_id uuid references generated_artifacts(artifact_id),
  verification_type text not null, -- human, rule, benchmark, explain, replay, unit_test
  status text not null, -- passed, failed, needs_review
  score numeric(8,4),
  notes text,
  created_at timestamptz not null default now()
);

create index verification_events_ai_status_idx on verification_events(ai_run_id, status, created_at desc);
create index verification_events_artifact_status_idx on verification_events(artifact_id, status, created_at desc);

-- -----------------------------
-- Query optimization / validation
-- -----------------------------

create table query_runs (
  query_run_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  source_node_id uuid references repo_nodes(node_id),
  sql_sha256 text not null,
  query_text text,
  engine text,
  status text not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  rows_read bigint,
  rows_written bigint,
  cpu_ms bigint,
  latency_ms bigint
);

create index query_runs_repo_status_idx on query_runs(repo_id, status, started_at desc);
create index query_runs_source_idx on query_runs(source_node_id, started_at desc);

alter table code_to_sql_edges
  add constraint code_to_sql_edges_query_run_fk
  foreign key (query_run_id) references query_runs(query_run_id);

create index code_to_sql_edges_query_run_idx on code_to_sql_edges(query_run_id) where query_run_id is not null;

create table explain_plans (
  explain_plan_id uuid primary key default gen_random_uuid(),
  query_run_id uuid references query_runs(query_run_id),
  plan_sha256 text not null,
  estimated_cost numeric(18,4),
  estimated_rows bigint,
  plan_json jsonb not null,
  captured_at timestamptz not null default now()
);

create index explain_plans_query_idx on explain_plans(query_run_id, captured_at desc);

create table optimizer_observations (
  optimizer_observation_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  query_run_id uuid references query_runs(query_run_id),
  observation_type text not null,
  observation_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index optimizer_observations_query_idx on optimizer_observations(query_run_id, observation_type, created_at desc);

create table index_advice (
  advice_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  proposed_by text not null, -- llm, dta, human, optimizer
  ai_run_id uuid references ai_runs(ai_run_id),
  target_table text not null,
  index_ddl text not null,
  reason text,
  status text not null default 'proposed', -- proposed, benchmarked, accepted, rejected, reverted
  created_at timestamptz not null default now()
);

create index index_advice_status_idx on index_advice(repo_id, proposed_by, status);
create index index_advice_ai_run_idx on index_advice(ai_run_id);

create table benchmark_runs (
  benchmark_run_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  benchmark_name text not null,
  workload_sha256 text,
  baseline_label text,
  candidate_label text,
  status text not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  metrics jsonb not null default '{}'::jsonb
);

create index benchmark_runs_repo_status_idx on benchmark_runs(repo_id, benchmark_name, status, started_at desc);

create table workload_replays (
  workload_replay_id uuid primary key default gen_random_uuid(),
  benchmark_run_id uuid references benchmark_runs(benchmark_run_id),
  workload_sha256 text,
  replay_engine text,
  status text not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  metrics jsonb not null default '{}'::jsonb
);

create index workload_replays_benchmark_idx on workload_replays(benchmark_run_id, status, started_at desc);

create table validation_results (
  validation_result_id uuid primary key default gen_random_uuid(),
  benchmark_run_id uuid references benchmark_runs(benchmark_run_id),
  advice_id uuid references index_advice(advice_id),
  decision text not null, -- accept, reject, needs_review
  reason text,
  created_at timestamptz not null default now()
);

create index validation_results_benchmark_idx on validation_results(benchmark_run_id, decision, created_at desc);
create index validation_results_advice_idx on validation_results(advice_id, decision, created_at desc);

-- -----------------------------
-- Vector and RAG evaluation
-- -----------------------------

create table vector_index_entries (
  vector_entry_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  node_id uuid not null references repo_nodes(node_id),
  embedding_model text not null,
  embedding_version text,
  chunk_sha256 text not null,
  dimensions integer,
  vector_store text,
  inserted_at timestamptz not null default now(),
  unique (node_id, embedding_model, embedding_version, chunk_sha256)
);

create index vector_index_entries_repo_model_idx on vector_index_entries(repo_id, embedding_model, embedding_version);

create table rag_eval_runs (
  rag_eval_run_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  eval_name text not null,
  dataset_sha256 text,
  chunker_version text,
  embedding_model text,
  reranker_model text,
  generator_model text,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  summary_metrics jsonb not null default '{}'::jsonb
);

create index rag_eval_runs_repo_started_idx on rag_eval_runs(repo_id, eval_name, started_at desc);

create table rerank_metrics (
  rerank_metric_id uuid primary key default gen_random_uuid(),
  rag_eval_run_id uuid not null references rag_eval_runs(rag_eval_run_id),
  query_id text not null,
  reranker_model text,
  ndcg_at_k numeric(8,4),
  latency_ms integer,
  created_at timestamptz not null default now()
);

create index rerank_metrics_eval_query_idx on rerank_metrics(rag_eval_run_id, query_id);

create table generation_metrics (
  generation_metric_id uuid primary key default gen_random_uuid(),
  rag_eval_run_id uuid not null references rag_eval_runs(rag_eval_run_id),
  query_id text not null,
  generator_model text,
  answer_sha256 text,
  latency_ms integer,
  output_tokens integer,
  created_at timestamptz not null default now()
);

create index generation_metrics_eval_query_idx on generation_metrics(rag_eval_run_id, query_id);

create table retrieval_metrics (
  retrieval_metric_id uuid primary key default gen_random_uuid(),
  rag_eval_run_id uuid not null references rag_eval_runs(rag_eval_run_id),
  query_id text not null,
  context_recall numeric(8,4),
  precision_at_k numeric(8,4),
  latency_ms integer,
  memory_mb numeric(12,2),
  update_cost_ms integer
);

create index retrieval_metrics_eval_query_idx on retrieval_metrics(rag_eval_run_id, query_id);

create table factuality_checks (
  factuality_check_id uuid primary key default gen_random_uuid(),
  rag_eval_run_id uuid not null references rag_eval_runs(rag_eval_run_id),
  query_id text not null,
  answer_sha256 text,
  groundedness numeric(8,4),
  factual_consistency numeric(8,4),
  verifier text,
  notes text
);

create index factuality_checks_eval_query_idx on factuality_checks(rag_eval_run_id, query_id);

-- -----------------------------
-- Future scale-out metadata
-- -----------------------------

create table project_shards (
  project_shard_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  shard_key text not null,
  shard_type text not null, -- repo, project, package, language, time
  placement text,
  created_at timestamptz not null default now()
);

create table router_rules (
  router_rule_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  rule_name text not null,
  shard_key text not null,
  route_expression text not null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (repo_id, rule_name)
);

create table replicas (
  replica_id uuid primary key default gen_random_uuid(),
  project_shard_id uuid references project_shards(project_shard_id),
  replica_name text not null,
  placement text,
  role text not null default 'follower',
  health text not null default 'unknown',
  updated_at timestamptz not null default now()
);

create table global_transaction_log (
  global_transaction_log_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  transaction_key text not null,
  status text not null,
  participant_summary jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table shard_rebalancing_events (
  shard_rebalancing_event_id uuid primary key default gen_random_uuid(),
  project_shard_id uuid references project_shards(project_shard_id),
  event_type text not null,
  reason text,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  metrics jsonb not null default '{}'::jsonb
);

create table package_groups (
  package_group_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  group_name text not null,
  language text,
  package_manager text,
  metadata jsonb not null default '{}'::jsonb,
  unique (repo_id, group_name)
);

create table heterogeneous_tables (
  heterogeneous_table_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  table_name text not null,
  workload_class text,
  schema_family text,
  metadata jsonb not null default '{}'::jsonb,
  unique (repo_id, table_name)
);

create table workload_classes (
  workload_class_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  class_name text not null,
  latency_target_ms integer,
  consistency_requirement text,
  routing_notes text,
  unique (repo_id, class_name)
);

create table cross_shard_queries (
  cross_shard_query_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  query_run_id uuid references query_runs(query_run_id),
  shard_count integer,
  status text not null,
  latency_ms bigint,
  created_at timestamptz not null default now()
);

create table neo4j_mirror_state (
  neo4j_mirror_state_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  graph_snapshot_id uuid references graph_snapshots(graph_snapshot_id),
  mirror_endpoint text,
  status text not null default 'not_configured',
  last_exported_at timestamptz,
  metrics jsonb not null default '{}'::jsonb
);

create table metadata_ranges (
  range_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  start_key text not null,
  end_key text not null,
  replica_count integer not null default 3,
  created_at timestamptz not null default now()
);

create table consensus_groups (
  consensus_group_id uuid primary key default gen_random_uuid(),
  range_id uuid references metadata_ranges(range_id),
  protocol text not null default 'raft',
  leader_node text,
  health text not null default 'unknown',
  updated_at timestamptz not null default now()
);

create table range_health_events (
  range_health_event_id uuid primary key default gen_random_uuid(),
  range_id uuid references metadata_ranges(range_id),
  health text not null,
  reason text,
  observed_at timestamptz not null default now(),
  evidence jsonb not null default '{}'::jsonb
);

create table leaseholders (
  leaseholder_id uuid primary key default gen_random_uuid(),
  range_id uuid references metadata_ranges(range_id),
  holder_node text not null,
  lease_start timestamptz not null,
  lease_end timestamptz,
  status text not null default 'active'
);

create table lease_transfer_events (
  lease_transfer_event_id uuid primary key default gen_random_uuid(),
  range_id uuid references metadata_ranges(range_id),
  from_holder text,
  to_holder text not null,
  reason text,
  transferred_at timestamptz not null default now()
);

create table multi_hop_query_log (
  multi_hop_query_log_id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(repo_id),
  query_pattern text not null,
  hop_count integer not null,
  engine text not null default 'postgres',
  latency_ms bigint,
  created_at timestamptz not null default now()
);
