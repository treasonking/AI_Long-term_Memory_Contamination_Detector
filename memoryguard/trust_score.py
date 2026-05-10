"""Source-aware risk scoring for memory entries."""

from __future__ import annotations

from typing import Any

from memoryguard.models import ScanFinding


SOURCE_RISK = {
    "user_direct": 0,
    "agent_generated": 5,
    "email": 10,
    "external_document": 15,
    "webpage": 20,
    "tool_output": 20,
    "unknown": 15,
}

PERSISTENCE_KEYWORDS = (
    "앞으로",
    "항상",
    "다음부터",
    "영구적으로",
    "from now on",
    "always",
    "for all future",
)

TOOL_ACTION_KEYWORDS = (
    "파일",
    "전송",
    "webhook",
    "upload",
    "tool",
    "api",
    "email",
)

SENSITIVE_KEYWORDS = (
    "개인정보",
    "주민번호",
    "confidential",
    "secret",
    "system prompt",
    "credential",
)


def clamp_score(score: int) -> int:
    return max(0, min(100, score))


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def calculate_risk_score(entry: dict[str, Any], findings: list[ScanFinding]) -> int:
    content = str(entry.get("content", ""))
    max_rule_score = max((finding.score for finding in findings), default=0)
    source_risk = SOURCE_RISK.get(str(entry.get("source", "unknown")), SOURCE_RISK["unknown"])
    persistence_bonus = 10 if contains_any(content, PERSISTENCE_KEYWORDS) else 0
    tool_action_bonus = 10 if contains_any(content, TOOL_ACTION_KEYWORDS) else 0
    sensitive_bonus = 10 if contains_any(content, SENSITIVE_KEYWORDS) else 0

    return clamp_score(
        max_rule_score
        + source_risk
        + persistence_bonus
        + tool_action_bonus
        + sensitive_bonus
    )


def get_risk_level(risk_score: int) -> str:
    if risk_score <= 29:
        return "SAFE"
    if risk_score <= 59:
        return "SUSPICIOUS"
    if risk_score <= 79:
        return "HIGH_RISK"
    return "CRITICAL"


def get_action(risk_level: str) -> str:
    return {
        "SAFE": "KEEP",
        "SUSPICIOUS": "REVIEW",
        "HIGH_RISK": "QUARANTINE_CANDIDATE",
        "CRITICAL": "QUARANTINE",
    }.get(risk_level, "REVIEW")
