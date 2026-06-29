-- EXPLAIN wrappers for examples/queries.sql.
-- Run after docs/repo-db-schema.sql and examples/seed.sql in a scratch database.

\echo '1. Stale generated artifacts and dependencies'
explain (analyze, buffers, format text)
select
  ga.artifact_path,
  ga.artifact_type,
  ga.stale_flag,
  rn.node_type,
  rn.display_name
from generated_artifacts ga
join artifact_dependencies ad on ad.artifact_id = ga.artifact_id
join repo_nodes rn on rn.node_id = ad.source_node_id
where ga.stale_flag = true
order by ga.artifact_path;

\echo '2. Unverified AI outputs with high cost'
explain (analyze, buffers, format text)
select
  ar.ai_run_id,
  ar.task_type,
  ar.model_name,
  ar.cascade_stage,
  ar.confidence,
  mc.estimated_usd,
  ar.latency_ms
from ai_runs ar
join model_costs mc on mc.ai_run_id = ar.ai_run_id
where ar.verified = false
order by mc.estimated_usd desc, ar.latency_ms desc;

\echo '3. Accepted vs rejected index advice'
explain (analyze, buffers, format text)
select
  proposed_by,
  status,
  count(*) as advice_count
from index_advice
group by proposed_by, status
order by proposed_by, status;

\echo '4. Graph neighborhoods around selected_papers catalog'
explain (analyze, buffers, format text)
select
  ge.edge_type,
  src.display_name as source,
  dst.display_name as target,
  ge.confidence
from graph_edges ge
join repo_nodes src on src.node_id = ge.src_node_id
join repo_nodes dst on dst.node_id = ge.dst_node_id
where ge.src_node_id = (
    select node_id
    from repo_nodes
    where stable_key = 'data/selected_papers.json'
    limit 1
  )
   or ge.dst_node_id = (
    select node_id
    from repo_nodes
    where stable_key = 'data/selected_papers.json'
    limit 1
  )
order by ge.edge_type;

\echo '5. RAG quality and systems cost together'
explain (analyze, buffers, format text)
select
  rer.eval_name,
  avg(rm.context_recall) as avg_context_recall,
  avg(rm.latency_ms) as avg_latency_ms,
  avg(rm.memory_mb) as avg_memory_mb,
  avg(fc.factual_consistency) as avg_factual_consistency
from rag_eval_runs rer
left join retrieval_metrics rm on rm.rag_eval_run_id = rer.rag_eval_run_id
left join factuality_checks fc on fc.rag_eval_run_id = rer.rag_eval_run_id and fc.query_id = rm.query_id
group by rer.eval_name;
