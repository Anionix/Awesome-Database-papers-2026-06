# Tencent

## Theme

Distributed design for heterogeneous multi-table workloads

## Adoptable idea

Plan for multiple languages, package managers, schema styles, artifact types, and workload classes in large monorepos.

## Why it matters

Large monorepos look like heterogeneous database workloads: many schemas, many access patterns, many teams, and uneven hotspots.

## Key papers / links

- [TDSQL-Boundless: A Distributed Database System for Large-scale Heterogeneous Multi-Table Workloads](https://dl.acm.org/doi/abs/10.1145/3788853.3803090) — ACM DOI
- [TDSQL-Boundless: A Distributed Database System for Large-scale Heterogeneous Multi-Table Workloads](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Use `project_shards`, `package_groups`, `heterogeneous_tables`, and workload-class routing for multi-language monorepo metadata.

## First schema objects

- `project_shards`
- `package_groups`
- `heterogeneous_tables`
- `workload_classes`
- `cross_shard_queries`

## Do now

Tag every file, package, generated artifact, and query with project, language, package manager, and workload class.

## Do later

Shard by project or package group when single-node metadata operations become a bottleneck.

## Caveat

Heterogeneity is a schema problem before it is a distributed-systems problem. Classify workload types early.

## Priority

P2
