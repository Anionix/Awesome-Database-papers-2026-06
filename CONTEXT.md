# Repository Context

This repository keeps a curated database-paper catalog and an implementation
playbook for repository metadata database design. `data/selected_papers.json` is
the canonical catalog data; generated catalog views are derived from it.

## Implemented Modules

The catalog scripts are split into lower modules and command adapters.

- `scripts/catalog_contract.py` owns the shared catalog contract vocabulary used
  by validation and generation: required record/source fields, accepted priority
  and claim-scope values, source labels, and identifier/date/url checks. It does
  not own paper facts; those remain in `data/selected_papers.json` and the linked
  source records.
- `scripts/catalog_surface.py` owns generated catalog surface planning and
  rendering for CSV, generated Markdown views, generated paper notes, README
  catalog table updates, and `manifest.json`.
- `scripts/sql_corpus.py` owns pure static SQL text introspection helpers. The
  SQL corpus itself remains in `docs/repo-db-schema.sql` and the SQL files under
  `examples/`.

Command adapters provide CLI wiring and repository checks:

- `scripts/generate_catalog.py`
- `scripts/validate_catalog.py`
- `scripts/check_sql.py`

Command adapters may import lower modules. Lower modules do not import command
adapters.
