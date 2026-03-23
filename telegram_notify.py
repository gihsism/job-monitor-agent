"""Telegram bot with inline Yes/No buttons for job approval."""

import json
import logging
from pathlib import Path

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

PENDING_JOBS_FILE = Path(__file__).parent / "data" / "pending_jobs.json"


def _load_pending() -> dict:
    if PENDING_JOBS_FILE.exists():
        return json.loads(PENDING_JOBS_FILE.read_text())
    return {}


def _save_pending(pending: dict):
    PENDING_JOBS_FILE.write_text(json.dumps(pending, indent=2))


def save_pending_job(job: dict):
    """Save a job to pending list so we can retrieve it when user clicks Yes."""
    pending = _load_pending()
    pending[job["id"]] = job
    _save_pending(pending)


def get_pending_job(job_id: str) -> dict | None:
    """Retrieve a pending job by ID."""
    pending = _load_pending()
    return pending.get(job_id)


def remove_pending_job(job_id: str):
    """Remove a job from pending list."""
    pending = _load_pending()
    pending.pop(job_id, None)
    _save_pending(pending)


async def send_job_for_review(bot: Bot, chat_id: str, job: dict):
    """Send a job posting with Yes/No inline buttons."""
    text = job.get("text", "")
    preview = text[:800] + "..." if len(text) > 800 else text

    track = "🎯 AI/PM" if job.get("is_primary") else "🏢 Accounting @ Tech"

    message = (
        f"🔔 <b>New Position Found</b>  [{track}]\n\n"
        f"<b>{job['title']}</b>\n\n"
        f"🔗 {job['url']}\n\n"
        f"📊 Relevance: {job['score']}\n\n"
        f"<b>Preview:</b>\n{preview}\n\n"
        f"<i>Interested? I'll tailor your CV + cover letter for this role.</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, tailor CV", callback_data=f"yes:{job['id']}"),
            InlineKeyboardButton("❌ Skip", callback_data=f"no:{job['id']}"),
        ]
    ])

    if len(message) > 4000:
        message = message[:4000] + "..."

    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def send_tailored_cv(bot: Bot, chat_id: str, job: dict, tailored_cv: dict,
                          cv_path: str, cover_letter_path: str = None):
    """Send the tailored CV and cover letter after user approved."""
    match_score = tailored_cv.get("match_score", "?")
    match_analysis = tailored_cv.get("match_analysis", "N/A")

    text = (
        f"📄 <b>CV Tailored!</b>\n\n"
        f"<b>{job['title']}</b>\n"
        f"🔗 {job['url']}\n\n"
        f"📊 Match Score: <b>{match_score}/100</b>\n"
        f"📝 {match_analysis}"
    )

    await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")

    if cv_path and Path(cv_path).exists():
        with open(cv_path, "rb") as f:
            await bot.send_document(
                chat_id=chat_id,
                document=f,
                caption=f"Tailored CV for: {job['title'][:200]}",
            )

    if cover_letter_path and Path(cover_letter_path).exists():
        with open(cover_letter_path, "rb") as f:
            await bot.send_document(
                chat_id=chat_id,
                document=f,
                caption=f"Cover letter for: {job['title'][:200]}",
            )


async def send_status(bot: Bot, chat_id: str, text: str):
    """Send a simple status message."""
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
