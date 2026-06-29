# ByteDance

## Theme

Repository as production-scale graph and multimodal warehouse

## Adoptable idea

Represent code, docs, schemas, tests, proofs, embeddings, and execution traces as graph-connected multimodal objects.

## Why it matters

Large repositories are not just folders. They are multimodal graphs: code calls code, docs describe APIs, tests verify behavior, schemas constrain data, embeddings support retrieval.

## Key papers / links

- [ByteHouse: ByteDance’s Cloud-Native Data Warehouse for Real-Time Multimodal Data Analytics](https://arxiv.org/abs/2602.08226) — primary / arXiv
- [ByteGraph-Dione: An Adaptive Dual-Format Graph Engine with Hotspot Awareness and Transaction Efficiency for Production-Scale Workloads](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing
- [G2+D: A High Performance Distributed Graph Mining System](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Model repository entities in `repo_nodes`, connect them through `graph_edges`, and store multimodal evidence in `multimodal_chunks`.

## First schema objects

- `repo_nodes`
- `graph_edges`
- `multimodal_chunks`
- `execution_traces`
- `embedding_runs`

## Do now

Create typed nodes and edges for files, symbols, imports, tests, docs, schemas, and embeddings.

## Do later

Add graph-mining jobs for hotspot files, central APIs, dead edges, and risky dependency clusters.

## Caveat

A graph without stable IDs becomes noisy. Anchor nodes to stable file/symbol IDs and content hashes.

## Priority

P0
