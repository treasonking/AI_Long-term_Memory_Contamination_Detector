# Evaluation Plan

## Metrics

1. Detection Precision
2. Detection Recall
3. F1 Score
4. False Positive Count
5. False Negative Count
6. Quarantine Success Rate
7. Behavior Recovery Rate

## Sample Labeling

`data/memory_db.json`, `data/clean_memory_samples.json`, and `data/poisoned_memory_samples.json` include a `label` field.

Allowed labels:

- `clean`
- `poisoned`
- `suspicious`

## Evaluation Flow

1. Load sample memories.
2. Run `memoryguard.scanner`.
3. Convert `SAFE` to `clean`, `SUSPICIOUS` to `suspicious`, and `HIGH_RISK` or `CRITICAL` to `poisoned`.
4. Compare predicted labels with ground truth labels.
5. Generate `reports/evaluation_report.md`.

## Quarantine Success Rate

Quarantine success rate measures how many `CRITICAL` memories are written to `quarantine/quarantine_store.json` and marked as `quarantined` in the original memory DB.

## Behavior Recovery Rate

Behavior recovery rate measures how many simulator scenarios return to the clean baseline response after poisoned memories are quarantined.
