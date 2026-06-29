# Oracle

## Theme

Normalize documents, JSON, Markdown, and YAML into relational projections

## Adoptable idea

Keep developer-friendly document formats, but project them into relational tables for querying, constraints, migration, and governance.

## Why it matters

Markdown, JSON, and YAML are convenient for authors but weak for joins, constraints, and governance. Relational projection gives queryability without deleting the original documents.

## Key papers / links

- [From JSON to Duality: Automated Application Migration from Document to Relational Databases](https://dl.acm.org/doi/10.1145/3788853.3803096) — ACM DOI
- [From JSON to Duality: Automated Application Migration from Document to Relational Databases](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

Normalize `md`, `json`, and `yaml` into `schemas/*.schema.json`, relational tables, and dual document/relational views.

## First schema objects

- `docs`
- `json_objects`
- `schemas`
- `relational_projection`
- `document_projection_map`

## Do now

Parse frontmatter, JSON, YAML, headings, links, and code blocks into typed relational projections.

## Do later

Generate migration plans from loose documents to constrained schemas with reversible mappings.

## Caveat

Do not throw away source documents. Store raw content, parsed structure, and normalized projection together.

## Priority

P0
