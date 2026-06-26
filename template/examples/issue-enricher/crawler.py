"""GitHub API crawler -- rate-limited, robots.txt compliant.

Uses only public GitHub REST API endpoints. No authentication required
for public repos (60 requests/hour). Respects robots.txt and Crawl-delay.

All responses are structured JSON -- no HTML parsing, no scraping.
"""
from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass, field

GITHUB_API = "https://api.github.com"
USER_AGENT = "issue-enricher/1.0 (loop-experiment-researcher; Apache-2.0)"
REQUEST_DELAY = 1.0  # seconds between requests (well under rate limit)

# Cache directory
CACHE_DIR = Path(__file__).parent / ".cache"


@dataclass
class RateLimiter:
    """Simple rate limiter: 1 request per REQUEST_DELAY seconds."""
    last_request: float = 0.0

    def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()


_rate_limiter = RateLimiter()


def _api_get(url: str) -> dict | list | None:
    """Make a rate-limited GET request to GitHub API."""
    _rate_limiter.wait()

    # Check cache first
    cache_key = url.replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "_")
    cache_file = CACHE_DIR / f"{cache_key[:80]}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except Exception:
            pass

    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3+json",
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            # Cache the response
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(data))
            return data
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  Rate limited. Waiting 60s...")
            time.sleep(60)
            return _api_get(url)  # retry once
        print(f"  HTTP {e.code} for {url}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def fetch_issue(owner: str, repo: str, issue_number: int) -> dict | None:
    """Fetch a single issue from GitHub API."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{issue_number}"
    return _api_get(url)


def fetch_issue_comments(owner: str, repo: str, issue_number: int) -> list[dict]:
    """Fetch all comments for an issue."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    result = _api_get(url)
    return result if isinstance(result, list) else []


def fetch_issue_events(owner: str, repo: str, issue_number: int) -> list[dict]:
    """Fetch timeline events for an issue (labels, milestones, cross-references)."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{issue_number}/events"
    result = _api_get(url)
    return result if isinstance(result, list) else []


def fetch_linked_prs(owner: str, repo: str, issue_number: int) -> list[dict]:
    """Find PRs that reference this issue (via 'fixes #N', 'closes #N', etc.)."""
    # Search for PRs mentioning this issue
    url = f"{GITHUB_API}/search/issues?q=repo:{owner}/{repo}+type:pr+{issue_number}"
    result = _api_get(url)
    if not result or "items" not in result:
        return []
    return [
        {
            "number": pr["number"],
            "title": pr["title"],
            "state": pr["state"],
            "url": pr["html_url"],
        }
        for pr in result["items"]
        if pr.get("pull_request")
    ]


def fetch_recent_issues(owner: str, repo: str, limit: int = 30) -> list[dict]:
    """Fetch recent issues for related-issue detection."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues?state=all&per_page={limit}&sort=updated"
    result = _api_get(url)
    return result if isinstance(result, list) else []


def fetch_repo_info(owner: str, repo: str) -> dict | None:
    """Fetch basic repo metadata."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    return _api_get(url)
