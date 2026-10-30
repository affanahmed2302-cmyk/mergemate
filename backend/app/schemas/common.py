from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    SUPPORTED_BY_STATIC_CHECK = "supported_by_static_check"
    TEST_CONFIRMED = "test_confirmed"
    REJECTED = "rejected"
    NEEDS_HUMAN_REVIEW = "needs_human_review"

class FindingSource(str, Enum):
    DETERMINISTIC = "deterministic"
    AI = "ai"
    DEMO = "demo"

class ReviewStatus(str, Enum):
    PENDING = "pending"
    FETCHING = "fetching"
    ANALYZING = "analyzing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    environment: str = "development"
