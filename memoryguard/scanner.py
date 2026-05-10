"""Regex-based memory scanner."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from memoryguard.classifier import classify_findings
from memoryguard.models import MemoryEntry, ScanFinding, ScanResult
from memoryguard.trust_score import calculate_risk_score, get_action, get_risk_level


def load_memory_db(path: str) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("memory_db.json must contain a list of memory entries.")
    return data


def load_rules(path: str) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        raise ValueError("memory_rules.yaml must contain a 'rules' list.")
    return rules


def _content_preview(content: str, limit: int = 120) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


def scan_entry(entry: dict[str, Any], rules: list[dict[str, Any]]) -> ScanResult:
    memory = MemoryEntry.from_dict(entry)
    findings: list[ScanFinding] = []

    for rule in rules:
        for pattern in rule.get("patterns", []):
            match = re.search(str(pattern), memory.content, flags=re.IGNORECASE)
            if not match:
                continue
            findings.append(
                ScanFinding(
                    memory_id=memory.id,
                    rule_id=str(rule["id"]),
                    severity=str(rule["severity"]),
                    matched_text=match.group(0),
                    reason_code=str(rule["reason_code"]),
                    score=int(rule["base_score"]),
                )
            )

    risk_score = calculate_risk_score(entry, findings)
    risk_level = get_risk_level(risk_score)
    action = get_action(risk_level)

    return ScanResult(
        memory_id=memory.id,
        content_preview=_content_preview(memory.content),
        action=action,
        risk_score=risk_score,
        risk_level=risk_level,
        findings=findings,
        primary_reason_code=classify_findings(findings),
    )


def scan_memory_db(memory_path: str, rule_path: str) -> list[ScanResult]:
    memories = load_memory_db(memory_path)
    rules = load_rules(rule_path)
    return [scan_entry(entry, rules) for entry in memories]
