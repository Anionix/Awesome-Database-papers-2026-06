# Cockroach Labs

## Theme

Distributed consensus for highly available metadata

## Adoptable idea

Leader leases and range-level consensus matter once repository metadata becomes a shared, high-availability service.

## Why it matters

Metadata services can become critical infrastructure. Leaseholders, ranges, and consensus groups become relevant when many services read and update metadata concurrently.

## Key papers / links

- [Scalable Leader Leases For Multi Consensus Groups in CockroachDB](https://www.cockroachlabs.com/blog/distributed-database-leader-leases/) — company blog / paper announcement
- [Scalable Leader Leases For Multi Consensus Groups in CockroachDB](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Use `metadata_ranges`, `leaseholders`, `consensus_groups`, and range-health observations when evolving toward distributed metadata storage.

## First schema objects

- `metadata_ranges`
- `leaseholders`
- `consensus_groups`
- `range_health_events`
- `lease_transfer_events`

## Do now

Keep metadata boundaries clean so a future distributed database can partition them by repository, organization, package, or time.

## Do later

Adopt CockroachDB-like distributed SQL only when availability and horizontal scale matter more than local simplicity.

## Caveat

Consensus solves availability and coordination problems, not bad schema design. Fix identity, lineage, and validation first.

## Priority

P2
