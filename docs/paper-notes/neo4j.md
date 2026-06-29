# Neo4j

## Theme

Use graph databases when multi-hop queries become the bottleneck

## Adoptable idea

Start with `graph_edges` in PostgreSQL, then mirror to Neo4j when multi-hop traversal and graph algorithms dominate workload cost.

## Why it matters

Repository graphs become valuable when questions require several hops: which tests cover a changed symbol, which docs mention it, which generated artifacts depend on it?

## Key papers / links

- [RIOT: Replicated Independently-Ordered Transactions](https://dl.acm.org/doi/10.1145/3788853.3803094) — ACM DOI
- [Neo4j Research: RIOT](https://neo4j.com/research/) — company research page
- [RIOT: Replicated Independently-Ordered Transactions](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Use PostgreSQL `graph_edges` first. Add a Neo4j mirror only after multi-hop queries, path ranking, or graph algorithms justify it.

## First schema objects

- `graph_edges`
- `graph_snapshots`
- `neo4j_mirror_state`
- `multi_hop_query_log`

## Do now

Store edges in a relational table with `src_id`, `dst_id`, `edge_type`, `source`, `valid_from`, and `confidence`.

## Do later

Export edges to Neo4j for path queries, centrality, community detection, and impact analysis.

## Caveat

Adding a graph DB too early creates operational overhead. Make the graph model portable first.

## Priority

P1
