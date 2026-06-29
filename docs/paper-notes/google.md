# Google

## Theme

Long-lived key-value / wide-column metadata design

## Adoptable idea

Optimize metadata identity for decades: stable keys, versioned paths, immutable content hashes, and forward-compatible columns.

## Why it matters

Repository metadata is historical by nature. Paths move, files rename, schemas evolve, and hashes remain the best anchor for content identity.

## Key papers / links

- [Twenty Years of Bigtable](https://research.google/pubs/twenty-years-of-bigtable/) — primary / Google Research
- [Twenty Years of Bigtable](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Use `file_id`, `path`, `sha256`, `version_id`, `valid_from`, `valid_to`, and `path_history` so metadata remains stable across renames and rebuilds.

## First schema objects

- `files`
- `file_versions`
- `path_history`
- `content_hashes`
- `metadata_cells`

## Do now

Separate logical file identity from mutable path and immutable content hash.

## Do later

Partition metadata by repository, time, and content-hash prefix for large-scale scans.

## Caveat

Do not use path as the only primary key. Paths are names, not identities.

## Priority

P0
