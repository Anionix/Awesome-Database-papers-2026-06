# AWS

## Theme

PostgreSQL-compatible horizontal scale

## Adoptable idea

Start with normal PostgreSQL semantics, then add router, shard, replica, and distributed transaction concepts only when scale demands it.

## Why it matters

Most repo metadata projects should begin with one reliable relational database. Horizontal scaling should preserve compatibility instead of forcing application-level sharding too early.

## Key papers / links

- [Aurora PostgreSQL Limitless Database: Building a Highly Scalable OLTP Database](https://www.amazon.science/publications/aurora-postgresql-limitless-database-building-a-highly-scalable-oltp-database) — primary / Amazon Science
- [Aurora PostgreSQL Limitless Database: Building a Highly Scalable OLTP Database](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Begin with single PostgreSQL. When repositories or organizations grow, introduce logical routers, project shards, replicas, and distributed transaction logs.

## First schema objects

- `router_rules`
- `project_shards`
- `replicas`
- `global_transaction_log`
- `shard_rebalancing_events`

## Do now

Design tables with stable IDs and clear shard keys, even before sharding is implemented.

## Do later

Route by organization, repository, package, or project boundary when metadata volume becomes large.

## Caveat

Avoid premature sharding. The first goal is correctness and compatibility; scale-out is a later migration path.

## Priority

P1
