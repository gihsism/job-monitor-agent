"""Job history tracking — records approved/skipped decisions and enables review."""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
HISTORY_FILE = DATA_DIR / "job_history.json"
EXPORT_FILE = DATA_DIR / "job_applications.csv"


def _load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def _save_history(history: list[dict]):
    DATA_DIR.mkdir(exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def record_decision(job: dict, decision: str, match_score: int | None = None):
    """Record a job decision (approved/skipped)."""
    history = _load_history()
    history.append({
        "title": job.get("title", ""),
        "url": job.get("url", ""),
        "score": job.get("score", 0),
        "decision": decision,
        "match_score": match_score,
        "decided_at": datetime.now().isoformat(),
        "query": job.get("query", ""),
    })
    _save_history(history)


def get_history(limit: int = 20) -> list[dict]:
    """Get recent job history entries."""
    history = _load_history()
    return history[-limit:]


def get_stats() -> dict:
    """Get summary statistics."""
    history = _load_history()
    approved = [h for h in history if h["decision"] == "approved"]
    skipped = [h for h in history if h["decision"] == "skipped"]
    return {
        "total": len(history),
        "approved": len(approved),
        "skipped": len(skipped),
        "approval_rate": f"{len(approved) / len(history) * 100:.0f}%" if history else "N/A",
    }


def export_csv() -> str:
    """Export job history to CSV. Returns file path."""
    history = _load_history()
    if not history:
        return ""

    DATA_DIR.mkdir(exist_ok=True)
    with open(EXPORT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "title", "url", "score", "decision", "match_score", "decided_at", "query"
        ])
        writer.writeheader()
        writer.writerows(history)

    return str(EXPORT_FILE)
