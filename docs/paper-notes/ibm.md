# IBM

## Theme

End-to-end benchmarking for RAG and embeddings

## Adoptable idea

Measure RAG as a whole system: embedding, indexing, retrieval, reranking, generation, latency, memory, update cost, and factual consistency.

## Why it matters

A repository knowledge base is useful only if retrieval quality and system cost are measured together. Recall alone is not enough.

## Key papers / links

- [RAGPerf: An End-to-End Benchmarking Framework for Retrieval-Augmented Generation Systems](https://arxiv.org/abs/2603.10765) — supporting benchmark / arXiv
- [Fabric-X: Scaling Hyperledger Fabric for Asset Exchange](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Persist `rag_eval_runs`, `context_recall`, `latency_ms`, `memory_mb`, `update_cost_ms`, `groundedness`, and `factual_consistency`.

## First schema objects

- `rag_eval_runs`
- `retrieval_metrics`
- `generation_metrics`
- `rerank_metrics`
- `factuality_checks`

## Do now

Benchmark at least five dimensions: recall, answer quality, latency, memory, and index update cost.

## Do later

Run benchmark suites whenever embedding model, chunker, index, or reranker changes.

## Caveat

RAG quality can improve while latency or update cost becomes unacceptable. Track both quality and systems metrics.

## Priority

P1
