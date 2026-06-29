# Contributing

This repository is curated, not exhaustive.

## Before you start

Use `data/selected_papers.json` as the canonical source. The CSV, source links, topic map, curated table, paper notes, README catalog table, and manifest are generated or validated from that file.

```sh
make generate
make check
```

Add a new paper only when it changes at least one concrete design choice:

- a table or column;
- a validation rule;
- a benchmark metric;
- a system boundary;
- a migration path;
- an operational caveat.

## Required catalog fields

Every catalog entry must include:

- company or system;
- theme;
- adoptable idea;
- source records with provenance;
- why it matters;
- repo / DB translation;
- first schema objects;
- do now;
- do later;
- caveat;
- priority.

Every source record must include:

- `title`;
- `url`;
- `type`;
- `source_type`;
- `source_url`;
- `venue_or_track`;
- `doi_or_arxiv`;
- `last_verified`;
- `claim_scope`.

## Acceptance criteria

```sh
make check
```

If you edit `data/selected_papers.json`, also run:

```sh
make generate
git diff --exit-code
```

The final command should be run after committing or after checking that the generated diff is intentional.

## Quality bar

- Prefer official conference pages, publisher pages, arXiv, company research pages, or author pages.
- Do not copy paper text beyond short title-level references.
- Separate factual paper metadata from your own implementation interpretation.
- Keep mappings practical and testable.
- Keep schema/playbook changes executable where possible; if an object is future-only, say so explicitly.
