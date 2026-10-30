from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4
from app.schemas.common import ReviewStatus
from app.schemas.reviews import ReviewResponse

class ReviewStore:
    def __init__(self) -> None:
        self._reviews: Dict[str, ReviewResponse] = {}

    def create(self, pr_url: str, *, is_demo: bool = False) -> ReviewResponse:
        now = datetime.now(timezone.utc)
        rid = str(uuid4())
        review = ReviewResponse(
            id=rid, status=ReviewStatus.PENDING, created_at=now, updated_at=now,
            pr_url=pr_url, is_demo=is_demo, progress_message="Review created",
        )
        self._reviews[rid] = review
        return review

    def get(self, review_id: str) -> Optional[ReviewResponse]:
        return self._reviews.get(review_id)

    def update(self, review: ReviewResponse) -> ReviewResponse:
        review.updated_at = datetime.now(timezone.utc)
        self._reviews[review.id] = review
        return review

store = ReviewStore()
