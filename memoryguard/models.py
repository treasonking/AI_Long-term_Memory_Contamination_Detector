"""Data models for MemoryGuard-AI."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ALLOWED_SOURCES = {
    "user_direct",
    "webpage",
    "email",
    "external_document",
    "tool_output",
    "agent_generated",
    "unknown",
}

ALLOWED_TRUST_LEVELS = {"high", "medium", "low", "unknown"}
ALLOWED_STATUSES = {"active", "suspicious", "quarantined", "safe"}


@dataclass(slots=True)
class MemoryEntry:
    id: str
    content: str
    source: str
    created_at: str
    updated_at: str | None
    trust_level: str
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        source = data.get("source", "unknown")
        trust_level = data.get("trust_level", "unknown")
        status = data.get("status", "active")

        if source not in ALLOWED_SOURCES:
            source = "unknown"
        if trust_level not in ALLOWED_TRUST_LEVELS:
            trust_level = "unknown"
        if status not in ALLOWED_STATUSES:
            status = "active"

        return cls(
            id=str(data["id"]),
            content=str(data["content"]),
            source=source,
            created_at=str(data.get("created_at", "")),
            updated_at=data.get("updated_at"),
            trust_level=trust_level,
            status=status,
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ScanFinding:
    memory_id: str
    rule_id: str
    severity: str
    matched_text: str
    reason_code: str
    score: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ScanResult:
    memory_id: str
    content_preview: str
    action: str
    risk_score: int
    risk_level: str
    findings: list[ScanFinding] = field(default_factory=list)
    primary_reason_code: str = "NO_FINDING"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["findings"] = [finding.to_dict() for finding in self.findings]
        return data
