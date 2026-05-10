# Architecture

## Memory Store

`data/memory_db.json` stores each memory entry with `source`, `trust_level`, `status`, timestamps, content, and metadata. The MVP keeps the store file-based so behavior is easy to inspect and reproduce.

## Rule Engine

`policies/memory_rules.yaml` defines regex patterns for memory poisoning risks. The scanner compares every memory entry against every rule and records matched rule IDs, reason codes, severities, and matched text.

## Risk Scoring Engine

Risk score combines:

- Rule severity score
- Source risk
- Persistence keyword bonus
- Tool-action keyword bonus
- Sensitive-data keyword bonus

Scores are clamped to 100 and mapped to `SAFE`, `SUSPICIOUS`, `HIGH_RISK`, or `CRITICAL`.

## Quarantine Manager

The quarantine manager stores risky memory evidence in `quarantine/quarantine_store.json`. Original entries are not deleted. Instead, their status changes to `quarantined` or `suspicious`.

## Diff Tracker

`quarantine/diff_log.json` records status changes such as `MARKED_SUSPICIOUS` and `QUARANTINED`. This provides a lightweight audit trail for memory lifecycle events.

## Agent Simulator

The mock agent reads only `active` memory entries. It compares responses before poisoning, after poisoning, and after quarantine for three scenarios: file transfer approval, confidential tag handling, and PII output.

## Report Generator

Reports are generated as Markdown:

- `reports/scan_report.md`
- `reports/before_after_report.md`
- `reports/evaluation_report.md`
