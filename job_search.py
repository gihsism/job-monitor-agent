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
    MUST_HAVE_KEYWORDS,
    BOOST_KEYWORDS,
    NEGATIVE_KEYWORDS,
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


def _relevance_score(title: str, text: str) -> int:
    """Score a job posting's relevance. Higher is better. Negative means skip."""
    content = (title + " " + text).lower()

    # Must-have check
    for kw in MUST_HAVE_KEYWORDS:
        if kw.lower() not in content:
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
            results = exa.search_and_contents(
                query=query,
                num_results=10,
                start_published_date=start_date,
                text={"max_characters": 5000},
                highlights={"num_sentences": 5},
            )

            for result in results.results:
                jid = _job_id(result.url)
                if jid in seen:
                    continue

                title = result.title or ""
                text = result.text or ""
                highlights = ""
                if hasattr(result, "highlights") and result.highlights:
                    highlights = " ".join(result.highlights)

                score = _relevance_score(title, text + highlights)
                if score < 0:
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
