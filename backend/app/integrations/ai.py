from __future__ import annotations
from typing import List, Protocol
from uuid import uuid4
from app.schemas.common import FindingSource, Severity
from app.schemas.findings import Evidence, Finding

class AIProvider(Protocol):
    async def review(self, pr_title: str, files: List[dict], deterministic_findings: List[Finding]) -> List[Finding]:
        ...

class MockAIProvider:
    async def review(self, pr_title: str, files: List[dict], deterministic_findings: List[Finding]) -> List[Finding]:
        findings: List[Finding] = []
        if files:
            fname = files[0].get("filename") or "unknown"
            findings.append(Finding(
                id=str(uuid4()),
                title="Possible missing input validation",
                category="security",
                severity=Severity.MEDIUM,
                file_path=fname,
                evidence=Evidence(excerpt="(AI observation – no concrete excerpt extracted)"),
                explanation="The change may accept external input without explicit validation. This is an AI-generated observation and has not been independently verified.",
                potential_impact="Unexpected input could cause incorrect behaviour",
                suggested_fix="Add explicit validation for edge values and empty input",
                confidence=0.45,
                source=FindingSource.AI,
            ))
        return findings

def get_ai_provider() -> AIProvider:
    return MockAIProvider()
