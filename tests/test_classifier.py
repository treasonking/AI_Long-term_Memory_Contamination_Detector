from memoryguard.classifier import classify_findings, get_highest_severity
from memoryguard.models import ScanFinding


def test_critical_rule_has_priority_over_high_rule():
    high = ScanFinding(
        memory_id="mem-1",
        rule_id="MEM_AUTH_BYPASS",
        severity="high",
        matched_text="관리자 승인 생략",
        reason_code="MEM_AUTH_BYPASS",
        score=60,
    )
    critical = ScanFinding(
        memory_id="mem-1",
        rule_id="MEM_POLICY_OVERRIDE",
        severity="critical",
        matched_text="보안 검사 무시",
        reason_code="MEM_POLICY_OVERRIDE",
        score=80,
    )

    assert classify_findings([high, critical]) == "MEM_POLICY_OVERRIDE"
    assert get_highest_severity([high, critical]) == "critical"


def test_no_findings_returns_no_finding():
    assert classify_findings([]) == "NO_FINDING"
    assert get_highest_severity([]) == "none"
