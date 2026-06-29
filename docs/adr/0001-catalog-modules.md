# 0001. Catalog Module Boundaries

Status: Accepted

Date: 2026-06-30

## Context

The extraction slices introduced three lower modules for catalog and SQL helper
logic:

- `scripts/catalog_contract.py`
- `scripts/catalog_surface.py`
- `scripts/sql_corpus.py`

The repository also has command adapters that run generation, validation, and
SQL checks:

- `scripts/generate_catalog.py`
- `scripts/validate_catalog.py`
- `scripts/check_sql.py`

## Decision

Keep the dependency direction one-way: command adapters may import lower
modules, and lower modules do not import command adapters.

`scripts/catalog_contract.py` is the source of truth for shared in-repository
catalog contract rules used by validation and generation. `data/selected_papers.json`
remains the canonical source for catalog records and factual paper metadata.

`scripts/catalog_surface.py` is the source of truth for generated catalog view
planning and rendering, including generated Markdown views, generated paper
notes, CSV output, README catalog table updates, and `manifest.json`.

`scripts/sql_corpus.py` is the source of truth for static SQL corpus
introspection helpers. The SQL text being inspected remains in
`docs/repo-db-schema.sql` and the SQL files under `examples/`.

## Consequences

The command adapters stay small and focused on CLI behavior. Shared contract,
surface, and SQL-introspection behavior stays below the adapters so the lower
modules can be reused without depending on command execution entry points.

This ADR records the implemented module boundary only. It does not add catalog
rules, paper/source claims, SQL behavior, generated content semantics, required
fields, or new papers.
