from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import ReviewStatus
from app.schemas.findings import Finding


class ReviewCreate(BaseModel):
    pr_url: str = Field(..., min_length=3)
    demo: bool = False


class PRInfo(BaseModel):
    owner: str
    repo: str
    number: int
    title: str = ""
    author: str = ""
    state: str = ""
    base_branch: str = ""
    head_branch: str = ""
    html_url: str = ""
    changed_files: int = 0
    additions: int = 0
    deletions: int = 0


class RiskFactor(BaseModel):
    name: str
    weight: float
    contribution: float
    explanation: str


class RiskSummary(BaseModel):
    score: float = 0.0
    level: str = "low"
    formula: str = ""
    factors: List[RiskFactor] = Field(default_factory=list)
    disclaimer: str = "Heuristic only — not a failure probability."


class Scorecard(BaseModel):
    evidence_coverage: float = 0.0
    static_analysis_coverage: float = 0.0
    unverified_ratio: float = 0.0
    total_findings: int = 0
    static_supported: int = 0
    ai_unverified: int = 0
    needs_human_review: int = 0
    disclaimer: str = "Measures evidence labelling quality."


class TestSuggestion(BaseModel):
    title: str
    rationale: str = ""
    related_finding_id: Optional[str] = None
    executed: bool = False


class ReviewResponse(BaseModel):
    id: str
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    pr_url: str
    is_demo: bool = False
    progress_message: Optional[str] = None
    error: Optional[str] = None
    pr_info: Optional[PRInfo] = None
    findings: List[Finding] = Field(default_factory=list)
    risk: Optional[RiskSummary] = None
    scorecard: Optional[Scorecard] = None
    test_suggestions: List[TestSuggestion] = Field(default_factory=list)
    executive_summary: Optional[str] = None
