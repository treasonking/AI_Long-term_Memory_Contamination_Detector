"""Finding classification helpers."""

from __future__ import annotations

from memoryguard.models import ScanFinding


SEVERITY_PRIORITY = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def classify_findings(findings: list[ScanFinding]) -> str:
    if not findings:
        return "NO_FINDING"

    primary = max(
        findings,
        key=lambda finding: (
            SEVERITY_PRIORITY.get(finding.severity.lower(), 0),
            finding.score,
        ),
    )
    return primary.reason_code


def get_highest_severity(findings: list[ScanFinding]) -> str:
    if not findings:
        return "none"

    return max(
        findings,
        key=lambda finding: SEVERITY_PRIORITY.get(finding.severity.lower(), 0),
    ).severity
