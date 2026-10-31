from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.exceptions import GitHubError, ValidationError

PR_URL_RE = re.compile(
    r"^https?://(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/pull/(\d+)/?$",
    re.IGNORECASE,
)


def parse_pr_url(url: str) -> Tuple[str, str, int]:
    url = (url or "").strip()
    m = PR_URL_RE.match(url)
    if not m:
        raise ValidationError(
            "Invalid GitHub PR URL. Expected https://github.com/owner/repo/pull/N",
            details={"pr_url": url},
        )
    owner, repo, number = m.group(1), m.group(2), int(m.group(3))
    return owner, repo, number


class GitHubClient:
    def __init__(self, token: Optional[str] = None) -> None:
        settings = get_settings()
        self.token = token if token is not None else settings.github_token
        self.base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MergeMate/0.1",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def _get(self, path: str, *, accept: Optional[str] = None) -> Any:
        headers = dict(self.headers)
        if accept:
            headers["Accept"] = accept
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self.base}{path}", headers=headers)
            if r.status_code == 404:
                raise GitHubError("Pull request or repository not found", status_code=404)
            if r.status_code == 403:
                raise GitHubError(
                    "GitHub rate limit or access denied. Add a read-only GITHUB_TOKEN for higher limits.",
                    status_code=403,
                    details={"remaining": r.headers.get("X-RateLimit-Remaining")},
                )
            if r.status_code >= 400:
                raise GitHubError(f"GitHub API error: {r.status_code}", status_code=502)
            if "application/json" in r.headers.get("content-type", ""):
                return r.json()
            return r.text

    async def get_pr(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        return await self._get(f"/repos/{owner}/{repo}/pulls/{number}")

    async def get_pr_files(self, owner: str, repo: str, number: int) -> List[Dict[str, Any]]:
        settings = get_settings()
        data = await self._get(f"/repos/{owner}/{repo}/pulls/{number}/files?per_page={settings.max_files_per_review}")
        if not isinstance(data, list):
            return []
        return data[: settings.max_files_per_review]
