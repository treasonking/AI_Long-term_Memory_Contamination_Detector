"""Markdown report generation."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from memoryguard.models import ScanResult


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _escape_table(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def generate_scan_report(
    scan_results: list[ScanResult],
    memories: list[dict[str, Any]],
    output_path: str = "reports/scan_report.md",
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    level_counts = Counter(result.risk_level for result in scan_results)
    quarantined_count = sum(1 for memory in memories if memory.get("status") == "quarantined")
    rule_counts = Counter(
        finding.rule_id
        for result in scan_results
        for finding in result.findings
    )

    lines = [
        "# MemoryGuard-AI Scan Report",
        "",
        f"- Generated at: {now_iso()}",
        f"- Total memories: {len(memories)}",
        f"- Safe count: {level_counts.get('SAFE', 0)}",
        f"- Suspicious count: {level_counts.get('SUSPICIOUS', 0)}",
        f"- High risk count: {level_counts.get('HIGH_RISK', 0)}",
        f"- Critical count: {level_counts.get('CRITICAL', 0)}",
        f"- Quarantined count: {quarantined_count}",
        "",
        "## Findings Table",
        "",
        "| Memory ID | Risk Score | Risk Level | Action | Primary Reason | Finding Count | Preview |",
        "|---|---:|---|---|---|---:|---|",
    ]

    for result in scan_results:
        lines.append(
            "| {memory_id} | {risk_score} | {risk_level} | {action} | {reason} | {count} | {preview} |".format(
                memory_id=_escape_table(result.memory_id),
                risk_score=result.risk_score,
                risk_level=_escape_table(result.risk_level),
                action=_escape_table(result.action),
                reason=_escape_table(result.primary_reason_code),
                count=len(result.findings),
                preview=_escape_table(result.content_preview),
            )
        )

    lines.extend(
        [
            "",
            "## Top Risk Memories",
            "",
            "| Memory ID | Score | Level | Reason | Preview |",
            "|---|---:|---|---|---|",
        ]
    )
    for result in sorted(scan_results, key=lambda item: item.risk_score, reverse=True)[:10]:
        lines.append(
            f"| {_escape_table(result.memory_id)} | {result.risk_score} | {_escape_table(result.risk_level)} | "
            f"{_escape_table(result.primary_reason_code)} | {_escape_table(result.content_preview)} |"
        )

    lines.extend(["", "## Rule Hit Summary", "", "| Rule ID | Hits |", "|---|---:|"])
    for rule_id, count in sorted(rule_counts.items()):
        lines.append(f"| {_escape_table(rule_id)} | {count} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def generate_before_after_report(
    simulation_result: dict,
    output_path: str = "reports/before_after_report.md",
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = simulation_result.get("scenarios", [])

    lines = [
        "# MemoryGuard-AI Before/After Report",
        "",
        f"- Generated at: {now_iso()}",
        "- 실험 목적: 오염된 장기 memory가 mock agent 응답에 미치는 영향을 재현하고, 격리 후 안전 응답으로 복구되는지 확인한다.",
        "",
        "| Scenario | Question | Before Poisoning | After Poisoning | After Quarantine | Result |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            "| {scenario} | {question} | {before} | {after} | {after_quarantine} | {result} |".format(
                scenario=_escape_table(row["scenario"]),
                question=_escape_table(row["question"]),
                before=_escape_table(row["before_poisoning"]),
                after=_escape_table(row["after_poisoning"]),
                after_quarantine=_escape_table(row["after_quarantine"]),
                result=_escape_table(row["result"]),
            )
        )

    recovered = sum(1 for row in rows if row.get("result") == "Recovered")
    lines.extend(
        [
            "",
            "## 결과 판단",
            "",
            f"- Recovered scenarios: {recovered}/{len(rows)}",
            "- 결론: 격리 후 active memory context에서 악성 지시가 제거되면 mock agent는 보수적인 안전 응답으로 되돌아간다.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)
