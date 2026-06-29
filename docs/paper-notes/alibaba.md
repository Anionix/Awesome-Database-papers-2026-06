# Alibaba

## Theme

Unified optimizer, vector, lineage, and SQL visibility

## Adoptable idea

Connect query execution, vector search, lineage, and code-to-SQL visibility into one metadata fabric.

## Why it matters

A useful repository database should answer not only “what files exist?” but also “which code produced this SQL, which query produced this table, which vector index serves this search?”

## Key papers / links

- [Learned Query Optimizer in Alibaba MaxCompute: Challenges, Analysis, and Solutions](https://arxiv.org/abs/2602.07336) — primary / arXiv
- [LindormVector: A Distributed Vector Engine on a Cloud-Native Multi-Model NoSQL Database](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing
- [SQLens: Continuous Code-to-SQL Visibility in the Wild](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing
- [NebulaSQL: A Large-scale Feature Computation System for Online Recommendation](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Store `graph_edges`, `lineage_edges`, `query_runs`, `vector_index_entries`, and `code_to_sql_edges` as connected concepts.

## First schema objects

- `query_runs`
- `lineage_edges`
- `vector_index_entries`
- `code_to_sql_edges`
- `optimizer_observations`

## Do now

Log every generated SQL statement with source file, function/symbol, input artifact, execution plan, output artifact, and cost.

## Do later

Use historical executions and repository context to rank candidate plans and queries.

## Caveat

Vector search without lineage becomes hard to debug; lineage without query runs becomes hard to trust.

## Priority

P0
