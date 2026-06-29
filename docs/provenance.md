# Provenance

This repository separates two kinds of claims.

## Factual source metadata

Factual metadata comes from linked source records in `data/selected_papers.json`.

Examples:

- paper title;
- source URL;
- source type;
- venue or track;
- DOI or arXiv identifier;
- date the source was last verified;
- whether the source is a paper page, accepted-paper listing, company research page, or implementation interpretation source.

Factual source metadata belongs in each `key_papers` entry.

## Repository interpretation

Repository interpretation explains how a paper or system idea maps to a practical repository metadata database.

Examples:

- `adoptable_idea`;
- `why_it_matters`;
- `repo_db_translation`;
- `first_schema_objects`;
- `do_now`;
- `do_later`;
- `watch_out`.

These fields are maintained by this repository. They should be useful, conservative, and testable.

## Verification date

`last_verified` records the date this repository last checked that the source URL supported the catalog entry. It is not a guarantee that the external page will remain unchanged.

## Generated views

The canonical catalog is `data/selected_papers.json`. The following files are generated from it:

- `data/selected_papers.csv`;
- `docs/curated-table.md`;
- `docs/source-links.md`;
- `docs/topic-map.md`;
- `docs/paper-notes/*.md`;
- the catalog table in `README.md`;
- `manifest.json`.

Run `make generate` after changing canonical catalog data.
