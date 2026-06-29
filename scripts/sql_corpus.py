"""Pure static SQL text introspection helpers."""

from __future__ import annotations

import re

IDENTIFIER_RE = re.compile(r"[a-z][a-z0-9_]*")
CREATE_TABLE_RE = re.compile(r"\bcreate\s+table\s+([a-z][a-z0-9_]*)\b", flags=re.IGNORECASE)
CREATE_TABLE_BODY_RE = re.compile(
    r"\bcreate\s+table\s+([a-z][a-z0-9_]*)\s*\((.*?)\n\);",
    flags=re.IGNORECASE | re.DOTALL,
)
CREATE_INDEX_RE = re.compile(r"\bcreate\s+(?:unique\s+)?index\s+([a-z][a-z0-9_]*)\b", flags=re.IGNORECASE)
ADD_CONSTRAINT_RE = re.compile(r"\badd\s+constraint\s+([a-z][a-z0-9_]*)\b", flags=re.IGNORECASE)
REFERENCED_TABLE_RE = re.compile(
    r"\b(?:from|join|insert\s+into)\s+([a-z][a-z0-9_]*)\b",
    flags=re.IGNORECASE,
)
TABLE_LEVEL_SCHEMA_TERMS = {"constraint", "primary", "foreign", "unique", "check"}


def strip_line_comments(sql: str) -> str:
    return "\n".join(line.split("--", 1)[0] for line in sql.splitlines())


def table_names(sql: str) -> set[str]:
    return set(CREATE_TABLE_RE.findall(sql))


def index_names(sql: str) -> set[str]:
    return set(CREATE_INDEX_RE.findall(sql))


def constraint_names(sql: str) -> set[str]:
    return set(ADD_CONSTRAINT_RE.findall(sql))


def referenced_tables(sql: str) -> set[str]:
    return set(REFERENCED_TABLE_RE.findall(strip_line_comments(sql)))


def schema_identifiers(sql: str) -> set[str]:
    identifiers = set(table_names(sql))
    for _table_name, body in CREATE_TABLE_BODY_RE.findall(sql):
        for raw_line in strip_line_comments(body).splitlines():
            line = raw_line.strip().rstrip(",")
            if not line:
                continue
            name = line.split(None, 1)[0]
            if name in TABLE_LEVEL_SCHEMA_TERMS:
                continue
            if IDENTIFIER_RE.fullmatch(name):
                identifiers.add(name)
    return identifiers
