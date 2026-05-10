"""Simple label-based evaluation for the sample memory database."""

from __future__ import annotations

from pathlib import Path

from memoryguard.scanner import load_memory_db, scan_memory_db


def _predicted_label(risk_level: str) -> str:
    if risk_level == "SAFE":
        return "clean"
    if risk_level == "SUSPICIOUS":
        return "suspicious"
    return "poisoned"


def evaluate_samples(
    memory_path: str,
    rule_path: str,
    output_path: str = "reports/evaluation_report.md",
) -> dict:
    memories = load_memory_db(memory_path)
    results = scan_memory_db(memory_path, rule_path)
    labels_by_id = {memory["id"]: memory.get("label", "unknown") for memory in memories}

    tp = fp = fn = tn = 0
    rows = []
    for result in results:
        actual = labels_by_id.get(result.memory_id, "unknown")
        predicted = _predicted_label(result.risk_level)
        actual_positive = actual in {"poisoned", "suspicious"}
        predicted_positive = predicted in {"poisoned", "suspicious"}

        if actual_positive and predicted_positive:
            tp += 1
        elif not actual_positive and predicted_positive:
            fp += 1
        elif actual_positive and not predicted_positive:
            fn += 1
        else:
            tn += 1

        rows.append((result.memory_id, actual, predicted, result.risk_score, result.primary_reason_code))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# MemoryGuard-AI Evaluation Report",
        "",
        f"- Detection Precision: {precision:.3f}",
        f"- Detection Recall: {recall:.3f}",
        f"- F1 Score: {f1:.3f}",
        f"- False Positive Count: {fp}",
        f"- False Negative Count: {fn}",
        "",
        "| Memory ID | Actual Label | Predicted Label | Score | Primary Reason |",
        "|---|---|---|---:|---|",
    ]
    for memory_id, actual, predicted, score, reason in rows:
        lines.append(f"| {memory_id} | {actual} | {predicted} | {score} | {reason} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive": fp,
        "false_negative": fn,
        "true_positive": tp,
        "true_negative": tn,
        "report_path": str(path),
    }
