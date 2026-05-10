"""Append-only memory change tracking."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _read_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("diff log must contain a list.")
    return data


def append_diff_event(event: dict, diff_log_path: str) -> None:
    path = Path(diff_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    events = _read_log(path)

    if "event_id" not in event:
        event = {"event_id": f"diff-{len(events) + 1:03d}", **event}

    events.append(event)
    with path.open("w", encoding="utf-8") as file:
        json.dump(events, file, ensure_ascii=False, indent=2)
        file.write("\n")


def create_quarantine_event(
    memory_id: str,
    before_status: str,
    after_status: str,
    reason_code: str,
) -> dict:
    event_type = "QUARANTINED" if after_status == "quarantined" else "MARKED_SUSPICIOUS"
    return {
        "memory_id": memory_id,
        "event_type": event_type,
        "before_status": before_status,
        "after_status": after_status,
        "timestamp": now_iso(),
        "reason_code": reason_code,
    }
