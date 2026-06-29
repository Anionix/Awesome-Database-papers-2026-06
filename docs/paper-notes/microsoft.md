# Microsoft

## Theme

LLM recommendations must be validated by database tooling

## Adoptable idea

Use LLMs for proposal generation, but rely on EXPLAIN plans, replay, benchmarks, and optimizer tooling for acceptance.

## Why it matters

LLMs can suggest useful index or schema changes, but production databases need repeatable validation because model output has variance and can regress workloads.

## Key papers / links

- [Evaluating the Practical Effectiveness of LLM-Driven Index Tuning with Microsoft Database Tuning Advisor](https://arxiv.org/abs/2603.09181) — primary / arXiv
- [Bitmap Filtering in the Fabric Data Warehouse](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing
- [CoddSpeed: Hardware Accelerated Query Processing in Microsoft Fabric](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing
- [ConDABench: Interactive Evaluation of Language Models for Data Analysis](https://2026.sigmod.org/sigmod_industry_papers.shtml) — SIGMOD 2026 Industry listing

## Repo / DB translation

LLM-generated index/schema advice must pass `EXPLAIN`, benchmark runs, workload replay, and rollback checks before being merged.

## First schema objects

- `index_advice`
- `explain_plans`
- `benchmark_runs`
- `workload_replays`
- `validation_results`

## Do now

Create a gate: LLM proposal -> generated migration -> EXPLAIN delta -> benchmark -> replay -> approval.

## Do later

Train a local rule library from LLM-generated hypotheses that repeatedly pass validation.

## Caveat

Never merge index advice directly from a model. Treat it as a candidate patch, not a decision.

## Priority

P0
