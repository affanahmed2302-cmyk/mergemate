from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import FindingSource, Severity, VerificationStatus


class Evidence(BaseModel):
    excerpt: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    notes: Optional[str] = None


class ProofStep(BaseModel):
    """One step in the ProofLayer evidence chain / Review Replay."""
    step: int
    name: str
    status: str  # passed | failed | partial | skipped
    detail: str


class Finding(BaseModel):
    id: str
    title: str
    category: str = "general"
    severity: Severity = Severity.MEDIUM
    file_path: Optional[str] = None
    evidence: Evidence = Field(default_factory=Evidence)
    explanation: str = ""
    potential_impact: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    source: FindingSource = FindingSource.DETERMINISTIC
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    proof_steps: List[ProofStep] = Field(default_factory=list)
    feedback: Optional[str] = None  # useful | incorrect | disputed
