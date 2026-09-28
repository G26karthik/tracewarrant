# ADR-0008 Storage

Status: ACCEPTED

Date: 2026-09-28

## Context
Initial data fits bounded local files and has no multi-user query requirement.
## Requirements
Portable artifacts, source digest, low RAM, no default raw trace copies.
## Alternatives considered
JSON/JSONL; Parquet/DuckDB; SQLite; Postgres/vector DB.
## Decision
Use local JSON/JSONL for M1 with byte/span limits.
## Why
Graph analysis needs no service operations.
## Consequences
Large cohorts require partitioning or future streaming/columnar support.
## Risks
Parsed objects exceed file size; retained IDs can remain sensitive.
## Evidence
[Architecture](../../ARCHITECTURE.md).
## Reversal conditions
Add columnar storage for measured query needs, SQLite for indexing, a server only for demonstrated concurrent access.
