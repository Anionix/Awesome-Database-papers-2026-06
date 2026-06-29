-- Awesome Database Papers 2026-06
-- PostgreSQL-flavored starter DDL for a repository metadata database.
-- This schema is conceptual. Adapt data types, indexes, and partitioning for production.

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

create table path_history (
  path_history_id uuid primary key default gen_random_uuid(),
  file_id uuid not null references files(file_id),
  path text not null,
  valid_from timestamptz not null,
  valid_to timestamptz,
  unique (file_id, path, valid_from)
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

create table artifact_dependencies (
  artifact_id uuid not null references generated_artifacts(artifact_id),
  source_node_id uuid not null references repo_nodes(node_id),
  source_version_id uuid references file_versions(version_id),
  dependency_role text not null default 'source',
  primary key (artifact_id, source_node_id, dependency_role)
);

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

create table explain_plans (
  explain_plan_id uuid primary key default gen_random_uuid(),
  query_run_id uuid references query_runs(query_run_id),
  plan_sha256 text not null,
  estimated_cost numeric(18,4),
  estimated_rows bigint,
  plan_json jsonb not null,
  captured_at timestamptz not null default now()
);

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

create table validation_results (
  validation_result_id uuid primary key default gen_random_uuid(),
  benchmark_run_id uuid references benchmark_runs(benchmark_run_id),
  advice_id uuid references index_advice(advice_id),
  decision text not null, -- accept, reject, needs_review
  reason text,
  created_at timestamptz not null default now()
);

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

create table leaseholders (
  leaseholder_id uuid primary key default gen_random_uuid(),
  range_id uuid references metadata_ranges(range_id),
  holder_node text not null,
  lease_start timestamptz not null,
  lease_end timestamptz,
  status text not null default 'active'
);
