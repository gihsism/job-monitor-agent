"""Job search module using Exa API."""

import json
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path

from exa_py import Exa

from config import (
    SEARCH_QUERIES,
    SECONDARY_QUERIES,
    JOB_DOMAINS,
    MUST_HAVE_KEYWORD_GROUPS,
    BOOST_KEYWORDS,
    NEGATIVE_KEYWORDS,
    PROFILE_URL_PATTERNS,
    PROFILE_TITLE_KEYWORDS,
)

SEEN_JOBS_FILE = Path(__file__).parent / "data" / "seen_jobs.json"


def _load_seen_jobs() -> dict:
    if SEEN_JOBS_FILE.exists():
        return json.loads(SEEN_JOBS_FILE.read_text())
    return {}


def _save_seen_jobs(seen: dict):
    SEEN_JOBS_FILE.write_text(json.dumps(seen, indent=2))


def _job_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _normalize_title(title: str) -> str:
    """Normalize a title for duplicate detection."""
    import re
    t = title.lower().strip()
    # Remove common suffixes like "- LinkedIn", "| Indeed", etc.
    t = re.sub(r"\s*[-|–—]\s*(linkedin|indeed|glassdoor|jobs\.ch|jobup).*$", "", t)
    # Remove extra whitespace
    t = re.sub(r"\s+", " ", t)
    return t


def _is_duplicate(job_title: str, existing_jobs: list[dict]) -> bool:
    """Check if a job is a duplicate of one already found (same role, different board)."""
    from difflib import SequenceMatcher
    norm = _normalize_title(job_title)
    for existing in existing_jobs:
        existing_norm = _normalize_title(existing["title"])
        ratio = SequenceMatcher(None, norm, existing_norm).ratio()
        if ratio > 0.85:
            return True
    return False


def _is_profile_page(url: str, title: str) -> bool:
    """Detect if a URL/title is a person's profile, news article, or non-job page."""
    url_lower = url.lower()

    # LinkedIn: only allow /jobs/ URLs — reject posts, articles, profiles, company pages
    if "linkedin.com" in url_lower:
        if "/jobs/" not in url_lower and "/job/" not in url_lower:
            return True

    # Check URL patterns that indicate profiles/CVs
    for pattern in PROFILE_URL_PATTERNS:
        if pattern.lower() in url_lower:
            return True

    # Check title patterns that indicate non-job content
    title_lower = title.lower()
    for kw in PROFILE_TITLE_KEYWORDS:
        if kw.lower() in title_lower:
            return True

    return False


def _relevance_score(title: str, text: str) -> int:
    """Score a job posting's relevance. Higher is better. Negative means skip."""
    content = (title + " " + text).lower()

    # Must match at least one keyword group (PM track OR accounting track)
    matched_any_group = False
    for group in MUST_HAVE_KEYWORD_GROUPS:
        if any(kw.lower() in content for kw in group):
            matched_any_group = True
            break
    if not matched_any_group:
        return -1

    # Negative keywords check
    for kw in NEGATIVE_KEYWORDS:
        if kw.lower() in content:
            return -10

    score = 0
    for kw in BOOST_KEYWORDS:
        if kw.lower() in content:
            score += 1

    return score


def search_jobs(exa_api_key: str, days_back: int = 7) -> list[dict]:
    """Search for relevant jobs using Exa API. Returns list of new job dicts."""
    exa = Exa(api_key=exa_api_key)
    seen = _load_seen_jobs()
    new_jobs = []

    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    all_queries = [(q, True) for q in SEARCH_QUERIES] + [(q, False) for q in SECONDARY_QUERIES]

    for query, is_primary in all_queries:
        try:
            search_kwargs = dict(
                query=query,
                num_results=10,
                start_published_date=start_date,
                text={"max_characters": 5000},
                highlights={"num_sentences": 5},
            )
            if JOB_DOMAINS:
                search_kwargs["include_domains"] = JOB_DOMAINS

            results = exa.search_and_contents(**search_kwargs)

            for result in results.results:
                jid = _job_id(result.url)
                if jid in seen:
                    continue

                title = result.title or ""

                # Skip profiles, CVs, and news articles
                if _is_profile_page(result.url, title):
                    continue

                text = result.text or ""
                highlights = ""
                if hasattr(result, "highlights") and result.highlights:
                    highlights = " ".join(result.highlights)

                score = _relevance_score(title, text + highlights)
                if score < 0:
                    continue

                # Skip duplicates (same job on different boards)
                if _is_duplicate(title, new_jobs):
                    continue

                job = {
                    "id": jid,
                    "title": title,
                    "url": result.url,
                    "text": text[:3000],
                    "highlights": highlights[:1000],
                    "score": score,
                    "is_primary": is_primary,
                    "query": query,
                    "found_at": datetime.now().isoformat(),
                }

                new_jobs.append(job)
                seen[jid] = {
                    "title": title,
                    "url": result.url,
                    "found_at": job["found_at"],
                }

        except Exception as e:
            print(f"[WARN] Search failed for query '{query}': {e}")
            continue

    _save_seen_jobs(seen)

    # Sort by relevance score descending, primary first
    new_jobs.sort(key=lambda j: (-int(j["is_primary"]), -j["score"]))

    return new_jobs
