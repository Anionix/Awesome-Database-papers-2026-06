# Agent Instructions

This repository is a curated catalog and implementation playbook. Keep changes small, sourced, and reproducible.

## Core rules

- Do not add or redistribute paper PDFs.
- Treat `data/selected_papers.json` as the canonical catalog.
- Run `make check` before handing off any change.
- Run `make generate` after editing canonical catalog data.
- Keep generated files deterministic; do not hand-edit generated catalog views.
- Separate factual paper metadata from repository/database interpretation.
- Prefer official conference pages, publisher pages, arXiv, company research pages, and author pages.

## Adding or updating a paper

1. Edit `data/selected_papers.json`.
2. Include provenance for every source: `source_type`, `source_url`, `venue_or_track`, `doi_or_arxiv`, `last_verified`, and `claim_scope`.
3. Add a paper note only when human narrative beyond the generated skeleton is needed.
4. Run `make generate`.
5. Run `make check`.

## Schema and playbook changes

- If a catalog entry names a schema object, the SQL DDL should either define that table or the docs should mark it as a future extension.
- Keep starter PostgreSQL behavior first; distributed, graph, and vector-specific systems are optional until workload evidence justifies them.
- Example SQL should be runnable against `examples/seed.sql` without hidden parameters.
- For query/index optimization, capture `EXPLAIN (ANALYZE, BUFFERS)` output before and after the change. Use `CREATE INDEX CONCURRENTLY` for live databases; the starter DDL assumes an empty scratch database.

## Source wording

- Use source records for facts such as title, venue, DOI/arXiv ID, and accepted-paper listing.
- Use `repo_db_translation`, `do_now`, `do_later`, and `watch_out` for this repository's interpretation.
- Do not make implementation claims stronger than the linked source supports.
