# Snowflake

## Theme

AI operators inside the database optimizer

## Adoptable idea

Treat LLM/AI calls as first-class database operators with measurable cost, quality, confidence, and fallback behavior.

## Why it matters

Semantic SQL makes AI inference part of query execution. That means the repository database should not hide prompts, models, costs, confidence, or verification state in logs only; they belong in normalized tables.

## Key papers / links

- [Streaming Model Cascades for Semantic SQL](https://arxiv.org/abs/2604.00660) — primary / arXiv
- [Cortex AISQL: A Production SQL Engine for Unstructured Data](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

`ai_runs`, `model_costs`, `confidence`, `cascade_stage`, and `verified` should be stored alongside query and artifact metadata.

## First schema objects

- `ai_runs`
- `model_costs`
- `model_cascade_stages`
- `semantic_operator_results`
- `verification_events`

## Do now

Log every AI call with model, prompt hash, input row/object id, output hash, confidence, latency, token usage, price estimate, cascade stage, and verification status.

## Do later

Let the optimizer choose between small/fast model, large/oracle model, cached output, and human review based on cost and confidence.

## Caveat

Do not trust a semantic operator just because it returns an answer. Persist uncertainty and verification state so downstream artifacts can be rebuilt or invalidated.

## Priority

P0
