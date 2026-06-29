"""Catalog contract vocabulary shared by catalog command adapters."""

from __future__ import annotations

import datetime
import re
from typing import Any

REQUIRED_RECORD_FIELDS = {
    "company": str,
    "theme": str,
    "adoptable_idea": str,
    "key_papers": list,
    "why_it_matters": str,
    "repo_db_translation": str,
    "first_schema_objects": list,
    "do_now": str,
    "do_later": str,
    "watch_out": str,
    "priority": str,
}

# Mirrors schemas/selected-paper.schema.json so validation stays stdlib-only.
REQUIRED_SOURCE_FIELDS = {
    "title": str,
    "url": str,
    "type": str,
    "source_type": str,
    "source_url": str,
    "venue_or_track": str,
    "doi_or_arxiv": str,
    "last_verified": str,
    "claim_scope": str,
}

VALID_PRIORITIES = {"P0", "P1", "P2"}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}

VALID_CLAIM_SCOPES = {
    "paper metadata",
    "accepted-paper listing",
    "company research page",
    "implementation interpretation source",
}

SCHEMA_TERM_FIELDS = ("repo_db_translation",)

SOURCE_TYPE_LABELS = {
    "acm_doi": "ACM DOI",
    "amazon_science": "primary / Amazon Science",
    "arxiv": "primary / arXiv",
    "company_blog": "company blog / paper announcement",
    "company_research": "company research page",
    "google_research": "primary / Google Research",
    "sigmod_industry_listing": "SIGMOD 2026 Industry listing",
    "supporting_arxiv": "supporting benchmark / arXiv",
}

URL_RE = re.compile(r"^https://")
LAST_VERIFIED_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
BACKTICK_IDENTIFIER_RE = re.compile(r"`([a-z][a-z0-9_]*)`")
SCHEMA_OBJECT_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def priority_rank(priority: Any) -> int:
    return PRIORITY_ORDER.get(priority, 99)


def source_label(source: dict[str, Any]) -> str:
    # Prefer the human-facing `type` value because generated docs expose it.
    # `source_type` remains the machine-readable provenance classifier.
    if source.get("type"):
        return str(source["type"])
    source_type = str(source.get("source_type", ""))
    return SOURCE_TYPE_LABELS.get(source_type, source_type)


def is_valid_last_verified_date(value: str) -> bool:
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True
