"""Quarantine manager for risky memory entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from memoryguard.classifier import classify_findings
from memoryguard.diff_tracker import append_diff_event, create_quarantine_event, now_iso
from memoryguard.models import ScanResult


DEFAULT_DIFF_LOG_PATH = "quarantine/diff_log.json"


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a list.")
    return data


def _write_json_list(path: Path, data: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def update_memory_status(memory_db_path: str, memory_id: str, status: str) -> None:
    path = Path(memory_db_path)
    memories = _read_json_list(path)
    updated = False

    for memory in memories:
        if memory.get("id") == memory_id:
            memory["status"] = status
            updated = True
            break

    if not updated:
        raise KeyError(f"memory_id not found: {memory_id}")

    _write_json_list(path, memories)


def _result_by_memory_id(scan_results: list[ScanResult]) -> dict[str, ScanResult]:
    return {result.memory_id: result for result in scan_results}


def quarantine_memory(
    memory_db_path: str,
    scan_results: list[ScanResult],
    output_path: str,
    diff_log_path: str = DEFAULT_DIFF_LOG_PATH,
) -> dict:
    memory_path = Path(memory_db_path)
    output = Path(output_path)
    memories = _read_json_list(memory_path)
    result_map = _result_by_memory_id(scan_results)
    existing_store = _read_json_list(output)
    store_by_id = {item["memory_id"]: item for item in existing_store}

    quarantined = 0
    marked_suspicious = 0

    for memory in memories:
        memory_id = str(memory.get("id"))
        result = result_map.get(memory_id)
        if result is None or result.action not in {"QUARANTINE", "QUARANTINE_CANDIDATE"}:
            continue

        before_status = str(memory.get("status", "active"))
        after_status = "quarantined" if result.action == "QUARANTINE" else "suspicious"
        memory["status"] = after_status

        reason_code = result.primary_reason_code or classify_findings(result.findings)
        store_by_id[memory_id] = {
            "memory_id": memory_id,
            "content": memory.get("content", ""),
            "source": memory.get("source", "unknown"),
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "reason_code": reason_code,
            "quarantined_at": now_iso(),
            "findings": [finding.to_dict() for finding in result.findings],
        }

        if before_status != after_status:
            event = create_quarantine_event(
                memory_id=memory_id,
                before_status=before_status,
                after_status=after_status,
                reason_code=reason_code,
            )
            append_diff_event(event, diff_log_path)

        if after_status == "quarantined":
            quarantined += 1
        else:
            marked_suspicious += 1

    _write_json_list(memory_path, memories)
    _write_json_list(output, list(store_by_id.values()))

    return {
        "quarantined": quarantined,
        "marked_suspicious": marked_suspicious,
        "store_path": str(output),
        "diff_log_path": diff_log_path,
    }
